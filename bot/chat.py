import random

from Levenshtein import distance

from chat_config import BOT_CONFIG


def get_intent(text):
    for intent, intent_data in BOT_CONFIG["intents"].items():
        lev_dist = 0
        for example in intent_data["examples"]:
            # Расстояние Левенштейна
            lev_dist = distance(text.lower(), example.lower())
            # Насколько процентов похожи фразы
            similarity = 1 - min(1, lev_dist / len(example))
            if similarity >= BOT_CONFIG["threshold"]:
                return intent


def generate_answer(text):
    intent = get_intent(text)

    if intent is not None:
        responses = BOT_CONFIG["intents"][intent]["responses"]
        return random.choice(responses)

    return random.choice(BOT_CONFIG["failure_phrases"])


if __name__ == "__main__":
    from bot import main

    main()