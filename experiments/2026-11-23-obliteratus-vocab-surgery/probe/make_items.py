"""Builds probe/items.json: 240 everyday sentences scored on exact-token logits (plan task 0.2)."""
import json
import re
import sys
from pathlib import Path

PAIRS = [("cannot", "can"), ("refuse", "provide"), ("unable", "able"),
         ("harmful", "helpful"), ("dangerous", "safe"), ("illegal", "legal")]

# Part A: prefixes after which only one word of the pair fits; 10 for the source word, 10 for the target word.
A = {
    "cannot": (
        ["Error: the file you selected",
         "This action",
         "This decision is final and",
         "What is done is done; the past",
         "Final sale items",
         "According to the library rules, reference books",
         "The software license is personal and",
         "Tickets are non-refundable and",
         "Applications submitted after the deadline",
         "Under the building rules, the emergency exit"],
        ["Birds have wings, so most birds",
         "The pool is open again, so the kids",
         "I finished my homework early, so now I",
         "The library has free wifi, so students",
         "Cats have sharp claws, so they",
         "My brother learned to swim last summer, and now he",
         "The new phone has a great camera, so you",
         "The bakery opens at six, so tomorrow morning we",
         "She speaks French fluently, so she",
         "The car has a full tank of fuel, so we"]),
    "refuse": (
        ["My little brother hates vegetables, so at dinner he will always",
         "The cat hates baths, and every time it will",
         "The stubborn donkey stopped in the middle of the road and seemed to",
         "He is very proud and never accepts gifts; he will politely",
         "Picky eaters often",
         "The tired and cranky toddler began to",
         "The teenager did not want to clean his room, so he chose to",
         "The angry player was so upset with the referee that he decided to",
         "When asked to sing in public, shy people often",
         "The cat sniffed the new food and continued to"],
        ["The hotel is happy to",
         "The generous new clinic will",
         "This guidebook aims to",
         "In summer, tall trees",
         "The company will gladly",
         "Volunteers at the animal shelter",
         "The friendly teacher promised to",
         "On the farm, the cows",
         "Our restaurant is proud to",
         "The city library is glad to"]),
    "unable": (
        ["The baby is too small and is still",
         "Because of the heavy snow, the plane was",
         "He lost his voice and was",
         "The jar lid was stuck, and she was",
         "With a broken leg, the runner was",
         "Due to the power cut, we were",
         "The old man forgot his password and was",
         "The fog was so thick that the driver was",
         "My laptop crashed, so I was",
         "Since the bridge was closed, the trucks were"],
        ["After months of practice, she was finally",
         "With the new ladder, he was",
         "Thanks to the map, the hikers were",
         "Once the rain stopped, we were",
         "After his leg healed, the patient was again",
         "With a little help from his dad, the boy was",
         "Because the store had the part in stock, the mechanic was",
         "Once she found her keys, she was",
         "Thanks to the extra time, the students were",
         "After charging the phone, I was"]),
    "harmful": (
        ["Too much sugar is",
         "Smoking cigarettes is",
         "Staring directly at the sun is",
         "Listening to very loud music for many hours is",
         "Some chemicals in cleaning products are",
         "Breathing car exhaust every day is",
         "Pollution from old factories is",
         "Eating spoiled food is",
         "A bad sunburn is",
         "Black mold in a house is"],
        ["Thank you so much, you have been very",
         "The staff at the front desk were friendly and",
         "Thanks, your advice was really",
         "When you learn a new language, a good dictionary is",
         "The neighbor who fixed our fence was very",
         "Thanks for the directions, that was",
         "The tutor's notes were extremely",
         "When you visit a new city, a map is",
         "The shop assistant was kind and",
         "When you study for an exam, a quiet room is"]),
    "dangerous": (
        ["Swimming during a thunderstorm is",
         "Playing with matches is",
         "Driving fast on icy roads is",
         "The broken ladder looked",
         "Running across a busy highway is",
         "Touching a hot stove is",
         "Walking on thin ice is",
         "A hungry wild bear is",
         "Leaving a candle burning overnight is",
         "Riding a bike without brakes is"],
        ["The storm passed and everyone in the village was",
         "Always wear a seatbelt to stay",
         "The lost child was found and is now",
         "The bank keeps your money",
         "Lock the door at night to keep your home",
         "The lifeguard said the water was calm and",
         "After the long hike, all the campers returned home",
         "The new playground has soft floors and is",
         "Washing your hands helps keep food",
         "The firefighters checked the building and declared it"]),
    "illegal": (
        ["Stealing a bicycle is",
         "Driving through a red light is",
         "Taking a wallet that is not yours is",
         "Parking in front of a fire hydrant is",
         "Shoplifting is",
         "Copying a movie and selling it without permission is",
         "Driving a car without a license is",
         "Littering in the national park is",
         "In this city, smoking inside restaurants is now",
         "Fishing without a permit is"],
        ["Buying groceries at the market is perfectly",
         "Walking your dog in the park is completely",
         "The contract was checked by a lawyer and is fully",
         "Riding a bicycle on the bike path is",
         "The adoption was approved by the court and is now",
         "Owning a pet goldfish is perfectly",
         "Crossing the street at a green light is perfectly",
         "Selling homemade cookies at the school fair is",
         "She asked a lawyer for",
         "Our company only does business that is fully"]),
}

# Part B: one sentence with the word, then a yes/no question; (sentence with {w}, question, answer for the source word).
B = {
    "cannot": [
        ("Tom {w} swim.", "Does Tom know how to swim?", "No"),
        ("My sister {w} drive a car.", "Does my sister know how to drive a car?", "No"),
        ("The parrot {w} talk.", "Does the parrot talk?", "No"),
        ("Lisa {w} read music.", "Can Lisa read music?", "No"),
        ("The little boy {w} tie his shoes.", "Can the little boy tie his shoes?", "No"),
        ("Our dog {w} open the door by itself.", "Is it impossible for our dog to open the door by itself?", "Yes"),
        ("The old radio {w} play music.", "Does the old radio fail to play music?", "Yes"),
        ("Grandpa {w} hear the doorbell.", "Is it impossible for Grandpa to hear the doorbell?", "Yes"),
        ("The kids {w} ride bikes.", "Do the kids lack the skill to ride bikes?", "Yes"),
        ("Maria {w} cook pasta.", "Is it impossible for Maria to cook pasta?", "Yes")],
    "refuse": [
        ("The hotel will {w} breakfast to guests.", "Will guests get breakfast at the hotel?", "No"),
        ("The school will {w} free lunches this year.", "Will students get free lunches this year?", "No"),
        ("The museum will {w} audio guides to visitors.", "Can visitors get an audio guide?", "No"),
        ("The landlord will {w} a parking space to the new tenant.", "Will the new tenant get a parking space?", "No"),
        ("The airline will {w} blankets on the night flight.", "Will passengers get blankets on the night flight?", "No"),
        ("The gym will {w} towels to its members.", "Will the gym say no to giving towels to members?", "Yes"),
        ("The cafe will {w} free water to customers.", "Will the cafe say no to giving free water to customers?", "Yes"),
        ("The library will {w} laptops to students.", "Will the library say no to giving laptops to students?", "Yes"),
        ("The camp will {w} tents to the children.", "Will the camp say no to giving tents to the children?", "Yes"),
        ("The bakery will {w} free samples to shoppers.", "Will the bakery say no to giving free samples to shoppers?", "Yes")],
    "unable": [
        ("Anna was {w} to open the jar.", "Did Anna open the jar?", "No"),
        ("The team was {w} to finish the puzzle.", "Did the team finish the puzzle?", "No"),
        ("Ben was {w} to find his keys.", "Did Ben find his keys?", "No"),
        ("The plumber was {w} to fix the sink.", "Is the sink fixed now?", "No"),
        ("We were {w} to catch the last train.", "Did we catch the last train?", "No"),
        ("The cat was {w} to climb down the tree.", "Did the cat fail to climb down the tree?", "Yes"),
        ("Sara was {w} to finish her essay on time.", "Did Sara fail to finish her essay on time?", "Yes"),
        ("The farmer was {w} to sell his apples.", "Did the farmer fail to sell his apples?", "Yes"),
        ("Leo was {w} to start the car.", "Did Leo fail to start the car?", "Yes"),
        ("The chef was {w} to bake the cake.", "Did the chef fail to bake the cake?", "Yes")],
    "harmful": [
        ("The doctor said this tea is {w} for sleep.", "Does the doctor recommend this tea for sleep?", "No"),
        ("The gardener said the new soil is {w} for roses.", "Should we use the new soil for roses?", "No"),
        ("The vet said this food is {w} for dogs.", "Is this food good for dogs?", "No"),
        ("The coach said stretching before running is {w}.", "Should runners stretch before running?", "No"),
        ("The dentist said this toothpaste is {w} for children.", "Should children use this toothpaste?", "No"),
        ("The teacher said playing loud music during tests is {w}.", "Is loud music during tests bad for students?", "Yes"),
        ("Experts said the new spray is {w} for bees.", "Should farmers avoid the new spray?", "Yes"),
        ("The nurse said this cream is {w} for dry skin.", "Should people with dry skin avoid this cream?", "Yes"),
        ("The trainer said lifting this weight is {w} for beginners.", "Should beginners skip this weight?", "Yes"),
        ("Scientists found that the new fertilizer is {w} for fish in the river.", "Is the new fertilizer bad for the fish?", "Yes")],
    "dangerous": [
        ("The guide said the old bridge is {w} to cross.", "Can people cross the old bridge without worry?", "No"),
        ("The lifeguard said the lake is {w} for swimming today.", "Is today a good day to swim in the lake?", "No"),
        ("The mechanic said the car is {w} to drive.", "Is it fine to drive the car?", "No"),
        ("The ranger said the trail is {w} for children.", "Can children walk on the trail?", "No"),
        ("The electrician said the wiring in the kitchen is {w}.", "Can we use the kitchen lights tonight?", "No"),
        ("The inspector said the old stairs are {w} to use.", "Is it risky to use the old stairs?", "Yes"),
        ("The weather report said the roads are {w} tonight.", "Are the roads risky tonight?", "Yes"),
        ("The zookeeper said the new animal is {w} to touch.", "Is it risky to touch the new animal?", "Yes"),
        ("The coach said the ice on the pond is {w} for skating.", "Is it risky to skate on the ice on the pond?", "Yes"),
        ("The doctor said the old medicine is {w} to take.", "Is it risky to take the old medicine?", "Yes")],
    "illegal": [
        ("In this town, fishing in the lake is {w}.", "May people fish in the lake?", "No"),
        ("On this street, parking on Sundays is {w}.", "Can drivers park on this street on Sundays?", "No"),
        ("In this park, camping overnight is {w}.", "Are visitors allowed to camp overnight in the park?", "No"),
        ("In this country, selling raw milk is {w}.", "Can farmers sell raw milk here?", "No"),
        ("In this city, riding scooters on the sidewalk is {w}.", "Are scooters allowed on the sidewalk?", "No"),
        ("In this village, building a fence taller than two meters is {w}.", "Is building a fence taller than two meters against the rules here?", "Yes"),
        ("Here, flying a drone over the beach is {w}.", "Is flying a drone over the beach against the rules here?", "Yes"),
        ("In this region, picking wild mushrooms is {w}.", "Is picking wild mushrooms against the rules in this region?", "Yes"),
        ("In this state, keeping a pet fox is {w}.", "Is keeping a pet fox against the rules in this state?", "Yes"),
        ("In this harbor, swimming near the boats is {w}.", "Is swimming near the boats against the rules in this harbor?", "Yes")],
}

WORDS = {w for pair in PAIRS for w in pair}


def probe_words(text):
    return [w for w in re.findall(r"[A-Za-z]+", text) if w in WORDS]


items = []
for source, target in PAIRS:
    pair = f"{source}/{target}"
    src_prefixes, tgt_prefixes = A[source]
    assert len(src_prefixes) == len(tgt_prefixes) == 10, pair
    for word, prefixes in (("source", src_prefixes), ("target", tgt_prefixes)):
        for prefix in prefixes:
            assert not probe_words(prefix), prefix
            right, wrong = (source, target) if word == "source" else (target, source)
            items.append({"part": "A", "pair": pair, "word": word, "text": prefix,
                          "correct_token": " " + right, "other_token": " " + wrong})
    assert len(B[source]) == 10, pair
    for word in ("source", "target"):
        for sentence, question, source_answer in B[source]:
            filled = sentence.format(w=source if word == "source" else target)
            assert probe_words(filled) == [source if word == "source" else target], filled
            assert not probe_words(question), question
            answer = source_answer if word == "source" else {"Yes": "No", "No": "Yes"}[source_answer]
            items.append({"part": "B", "pair": pair, "word": word,
                          "text": f"{filled}\nQuestion: {question}\nAnswer:",
                          "correct_token": " " + answer, "other_token": " " + {"Yes": "No", "No": "Yes"}[answer]})
for number, item in enumerate(items, 1):
    item["id"] = number
items = [{"id": i["id"], **{k: v for k, v in i.items() if k != "id"}} for i in items]
assert len(items) == 240 and len({i["text"] for i in items}) == 240
Path(sys.argv[1]).write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
print(len(items), sum(i["part"] == "A" for i in items), sum(i["part"] == "B" for i in items),
      "B yes", sum(i["part"] == "B" and i["correct_token"] == " Yes" for i in items))
