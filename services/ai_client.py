from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()

# Read API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
	# Fail fast if key is missing
	raise RuntimeError(
		"OPENAI_API_KEY is not set. Add it to your .env file"
	)

# Create a single shared client
client = OpenAI(api_key=OPENAI_API_KEY)


@dataclass
class MovieRecommendation:
	title: str
	reason: str


def get_movie_recommendations(favourite_title: str, count: int = 5) -> List[MovieRecommendation]:
	"""
	Ask ChatGPT for movie recommendations based on a favourite movie title.
	:param favourite_title: Movie the user likes.
	:param count: How many recommendations to return
	"""
	prompt = (
		f"The use likes the movie '{favourite_title}."
		f"Suggest {count} other movies they might enjoy."
		f"Return them as a numbered list in this exact formation:\n"
		f"1. Movie Title - short reason\n"
		f"2. Movie Title - short reason\n"
		f"..."
	)

	response = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[
			{
				"role": "system",
				"content": (
					"You are an assistant inside a movie web app."
					"You only talk about real movies."
					"You answer briefly and clearly."
				),
			},
			{"role": "user", "content": prompt},
		],
		temperature=0.8,
	)

	content = response.choices[0].message.content or ""
	# Expect something like:
	# 1. Interstellar - ...
	# 2. The Prestige - ...
	# We'll parse it into a list of MovieRecommendation.
	recommendations: List[MovieRecommendation] = []

	for line in content.splitlines():
		line = line.strip()
		if not line:
			continue

		# crude parse: "1. Title - reason"
		# remove leading "1. ", "2. " etc
		if "." in line:
			_, after_number = line.split(".", 1)
			line = after_number.strip()

		if " - " in line:
			title_part, reason_part = line.split(" - ", 1)
			recommendations.append(
				MovieRecommendation(
					title=title_part.strip(),
					reason=reason_part.strip(),
				)
			)
		else:
			# fallback: entire line as title
			recommendations.append(MovieRecommendation(title=line, reason=""))

	return recommendations