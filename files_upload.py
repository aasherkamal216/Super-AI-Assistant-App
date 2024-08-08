[
  {
    "role": "user",
    "parts": [
      "Please Answer what is asked in the audio."
    ]
  },
  {
    "role": "model",
    "parts": [
      "Please provide me with the audio file or a transcript of the audio. I need to hear or read the audio to understand what is being asked.  \n"
    ]
  },
  {
    "role": "user",
    "parts": [
      "who is halaku khan"
    ]
  },
  {
    "role": "model",
    "parts": [
      "Hulagu Khan (c. 1217 – 1265) was a grandson of Genghis Khan and the founder of the Ilkhanate, a Mongol-led state that ruled Persia and parts of Mesopotamia, Anatolia, and the Caucasus from the mid-13th to the early 14th centuries. \n\nHere are some key points about Hulagu Khan:\n\n* **Military Leader:** He was a skilled military commander who led the Mongol conquest of the Middle East. He was responsible for the sacking of Baghdad in 1258, which marked the end of the Abbasid Caliphate. \n* **Expansion and Conquest:** Under his rule, the Mongol Empire expanded significantly, conquering vast territories in the Middle East. \n* **Patron of the Arts and Sciences:** Despite his brutality, Hulagu Khan was also a patron of the arts and sciences. He encouraged the development of Persian culture and scholarship. \n* **Religious Tolerance:** He generally practiced religious tolerance, allowing different religious groups to coexist within his empire. \n* **Legacy:** Hulagu Khan's legacy is complex. He is remembered as a ruthless conqueror but also as a ruler who contributed to the development of Persian culture and the spread of Mongol influence in the Middle East.\n\nHis conquests and reign had a profound impact on the history of the Middle East, marking a turning point in the region's political and cultural landscape. \n"
    ]
  },
  {
    "role": "user",
    "parts": [
      "Who was Avicenna"
    ]
  },
  {
    "role": "model",
    "parts": [
      "Avicenna, also known as Ibn Sina, was a Persian polymath, physician, philosopher, and scholar who lived during the Islamic Golden Age (980-1037). He was born in Bukhara, modern-day Uzbekistan, and became one of the most influential thinkers of the medieval period.\n\nHere are some key aspects of his life and contributions:\n\n**Scholarly Achievements:**\n\n* **Medicine:** Avicenna is best known for his monumental work \"The Canon of Medicine,\" which became a standard medical textbook for centuries in both the Islamic world and Europe. It covered a wide range of medical topics, including anatomy, physiology, pharmacology, and surgery.\n* **Philosophy:** He was a prominent philosopher who wrote extensively on logic, metaphysics, ethics, and politics. He developed his own philosophical system, influenced by Aristotle and other Greek thinkers.\n* **Science:** Avicenna made significant contributions to astronomy, geology, and psychology. He wrote about the movement of the stars, the formation of mountains, and the nature of the human soul.\n\n**Impact and Legacy:**\n\n* **Medical Education:** His \"Canon of Medicine\" was translated into Latin and used in European medical schools for centuries, influencing the development of Western medicine.\n* **Philosophical Influence:** His philosophical ideas influenced later thinkers, including Thomas Aquinas and Maimonides.\n* **Cultural Significance:** Avicenna is considered a national hero in Persia and a prominent figure in the history of Islamic thought.\n\n**Key Points:**\n\n* Avicenna was a polymath who excelled in various fields, including medicine, philosophy, science, and literature.\n* His \"Canon of Medicine\" was a groundbreaking medical textbook that shaped medical practice for centuries.\n* He was a prominent philosopher who developed his own philosophical system.\n* His work had a lasting influence on both the Islamic world and Europe.\n\nAvicenna's contributions to knowledge and scholarship continue to be studied and admired today. He"
    ]
  },
  {
    "role": "user",
    "parts": [
      "<PIL.PngImagePlugin.PngImageFile image mode=RGBA size=512x512 at 0x201DB05C380>",
      "Please Answer what is asked in the audio."
    ]
  },
  {
    "role": "model",
    "parts": [
      "Please provide me with the audio file or a transcript of the audio. I need to hear or read the audio to understand what is being asked.  I can't see or hear anything from the image you provided. \n"
    ]
  },
  {
    "role": "user",
    "parts": [
      "Please Answer what is asked in the audio."
    ]
  },
  {
    "role": "model",
    "parts": [
      "I am unable to process audio. I am a text-based chat assistant and thus I cannot hear or analyze any audio. \n"
    ]
  },
  {
    "role": "user",
    "parts": [
      "<PIL.PngImagePlugin.PngImageFile image mode=RGBA size=512x512 at 0x201DB05E870>",
      "what is this"
    ]
  },
  {
    "role": "model",
    "parts": [
      "This is a cartoon image of a robot. \n"
    ]
  },
  {
    "role": "user",
    "parts": [
      "<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=141x115 at 0x201DB05E690>",
      "what do you see "
    ]
  }
]

import asyncio

from edge_tts import list_voices

async def print_voices() -> None:
    """Print all available voices."""
    voices = await list_voices()
    voices = sorted(voices, key=lambda voice: voice["ShortName"])
    print("| Name | Gender | Language |")
    print("| :--- | :----- | :--------|")
    for idx, voice in enumerate(voices):
        if idx != 0:
            pass

        cols = None
        for key in voice.keys():
            if key in (
                "SuggestedCodec",
                "FriendlyName",
                "Status",
                "VoiceTag",
                "Name",
                "Locale",
            ):
                continue
            pretty_key_name = key if key != "ShortName" else "Name"
            if pretty_key_name == 'Name':
                cols = []
            cols.append(voice[key])

            if pretty_key_name == 'Gender':
                print(f"| {cols[0]} | {cols[1]} |  {'-'.join(cols[0].split('-')[0:2])}  |")

if __name__ == "__main__":
    asyncio.run(print_voices())