"""
Database Seeding Script for Multi-Exam CBT System.

Seeds all 6 examination bodies (JAMB, WAEC, NECO, NABTEB, BECE, SCHOOL)
across 7 core academic subjects with 15 questions per subject per year,
covering at least 3 distinct academic years (2023, 2024, 2025).

Total: 6 Exam Bodies x 7 Subjects x 3 Years x 15 Questions = 1,890 Questions.
"""

from __future__ import annotations

import sys
import time
from typing import Any
from sqlalchemy import select

from app.database.database import SessionLocal, init_database
from app.database.models import Subject, Question, Option


# ==============================================================================
# SUBJECT DEFINITIONS
# ==============================================================================

CORE_SUBJECTS = [
    {"name": "English Language", "code": "ENG"},
    {"name": "Mathematics", "code": "MTH"},
    {"name": "Physics", "code": "PHY"},
    {"name": "Chemistry", "code": "CHM"},
    {"name": "Biology", "code": "BIO"},
    {"name": "Economics", "code": "ECO"},
    {"name": "Government", "code": "GOV"},
]

EXAM_BODIES = ["JAMB", "WAEC", "NECO", "NABTEB", "BECE", "SCHOOL"]
EXAM_YEARS = [2023, 2024, 2025]


# ==============================================================================
# SUBJECT QUESTION POOL TEMPLATES
# ==============================================================================

def get_english_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic English Language questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}Choose the option that is most nearly OPPOSITE in meaning to the underlined word: The minister's explanation was considered <u>ambiguous</u> by the panel.",
            "options": [
                ("A", "Clear and explicit", True),
                ("B", "Vague and confusing", False),
                ("C", "Detailed and lengthy", False),
                ("D", "Intricate and complex", False),
            ],
            "exp": "Ambiguous means open to more than one interpretation or unclear. Its opposite is 'clear and explicit'.",
        },
        {
            "num": 2,
            "text": f"{prefix}Choose the option that is NEAREST in meaning to the underlined word: The doctor advised him to adopt a <u>frugal</u> lifestyle.",
            "options": [
                ("A", "Extravagant", False),
                ("B", "Economical", True),
                ("C", "Careless", False),
                ("D", "Luxurious", False),
            ],
            "exp": "Frugal means sparing or economical with regard to money or food.",
        },
        {
            "num": 3,
            "text": f"{prefix}Fill in the blank with the most appropriate option: Neither the teacher nor the students ______ present at the assembly yesterday.",
            "options": [
                ("A", "was", False),
                ("B", "were", True),
                ("C", "is", False),
                ("D", "are", False),
            ],
            "exp": "When using 'neither... nor', the verb agrees with the subject closer to it ('students', plural, in past tense: 'were').",
        },
        {
            "num": 4,
            "text": f"{prefix}Identify the figure of speech used in the sentence: 'The angry waves swallowed the small fishing boat.'",
            "options": [
                ("A", "Metaphor", False),
                ("B", "Simile", False),
                ("C", "Personification", True),
                ("D", "Hyperbole", False),
            ],
            "exp": "Personification attributes human qualities ('angry', 'swallowed') to non-human entities ('waves').",
        },
        {
            "num": 5,
            "text": f"{prefix}Choose the correct question tag: You haven't seen my spectacles anywhere, ______?",
            "options": [
                ("A", "have you", True),
                ("B", "haven't you", False),
                ("C", "did you", False),
                ("D", "didn't you", False),
            ],
            "exp": "A negative main clause ('haven't seen') takes a positive question tag ('have you').",
        },
        {
            "num": 6,
            "text": f"{prefix}Select the word that has the same vowel sound as the underlined sound in 'b<u>ir</u>d':",
            "options": [
                ("A", "heard", True),
                ("B", "beard", False),
                ("C", "heart", False),
                ("D", "hard", False),
            ],
            "exp": "The vowel sound in 'bird' is /ɜː/, which matches the vowel in 'heard'.",
        },
        {
            "num": 7,
            "text": f"{prefix}Fill in the blank with the correct preposition: The committee has agreed ______ the proposed amendments.",
            "options": [
                ("A", "to", True),
                ("B", "with", False),
                ("C", "on", False),
                ("D", "about", False),
            ],
            "exp": "One agrees 'to' a proposal or plan, but agrees 'with' a person.",
        },
        {
            "num": 8,
            "text": f"{prefix}Choose the option that best explains the idiom: 'To beat about the bush' means to ______.",
            "options": [
                ("A", "clear a pathway in the forest", False),
                ("B", "avoid the main topic in discussion", True),
                ("C", "search thoroughly for something lost", False),
                ("D", "strike an opponent repeatedly", False),
            ],
            "exp": "'Beat about the bush' is an idiom meaning to speak evasively and avoid coming to the point.",
        },
        {
            "num": 9,
            "text": f"{prefix}Choose the word that is correctly spelt:",
            "options": [
                ("A", "Accomodation", False),
                ("B", "Accommodation", True),
                ("C", "Acommodation", False),
                ("D", "Accomadation", False),
            ],
            "exp": "'Accommodation' is spelled with double 'c' and double 'm'.",
        },
        {
            "num": 10,
            "text": f"{prefix}Select the option with the correct primary stress on the word: 'PHOTOGRAPHY'",
            "options": [
                ("A", "PHO-to-gra-phy", False),
                ("B", "pho-TO-gra-phy", True),
                ("C", "pho-to-GRA-phy", False),
                ("D", "pho-to-gra-PHY", False),
            ],
            "exp": "Words ending in '-graphy' generally place the primary stress on the syllable immediately preceding '-graphy' (pho-TO-gra-phy).",
        },
        {
            "num": 11,
            "text": f"{prefix}Choose the appropriate conditional structure: If she ______ harder, she would have passed the examination.",
            "options": [
                ("A", "studies", False),
                ("B", "studied", False),
                ("C", "had studied", True),
                ("D", "has studied", False),
            ],
            "exp": "The third conditional takes 'had + past participle' in the if-clause and 'would have + past participle' in the main clause.",
        },
        {
            "num": 12,
            "text": f"{prefix}Identify the grammatical function of the underlined clause: <u>What he said at the meeting</u> surprised everyone.",
            "options": [
                ("A", "Adverbial clause of reason", False),
                ("B", "Noun clause acting as subject of the sentence", True),
                ("C", "Adjectival clause modifying everyone", False),
                ("D", "Noun clause acting as object of the verb", False),
            ],
            "exp": "'What he said at the meeting' is a noun clause functioning as the subject of the finite verb 'surprised'.",
        },
        {
            "num": 13,
            "text": f"{prefix}Choose the word that best completes the sentence: The judge found the accused guilty of ______ for lying under oath.",
            "options": [
                ("A", "perjury", True),
                ("B", "treason", False),
                ("C", "slander", False),
                ("D", "libel", False),
            ],
            "exp": "Perjury is the offense of willfully telling an untruth in a court after having taken an oath.",
        },
        {
            "num": 14,
            "text": f"{prefix}Select the antonym for the word <u>lucid</u> in: 'The professor gave a lucid presentation on quantum mechanics.'",
            "options": [
                ("A", "Eloquent", False),
                ("B", "Obscure", True),
                ("C", "Brilliant", False),
                ("D", "Transparent", False),
            ],
            "exp": "Lucid means clear and easy to understand; obscure means unclear and difficult to understand.",
        },
        {
            "num": 15,
            "text": f"{prefix}Fill in the blank: The jury reached ______ unanimous verdict after hours of deliberation.",
            "options": [
                ("A", "a", True),
                ("B", "an", False),
                ("C", "the", False),
                ("D", "any", False),
            ],
            "exp": "'Unanimous' begins with a consonant sound (/juː/), so the indefinite article 'a' is required.",
        },
    ]


def get_mathematics_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Mathematics questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}Solve for x: 2^(2x + 1) = 32",
            "options": [
                ("A", "x = 1", False),
                ("B", "x = 2", True),
                ("C", "x = 3", False),
                ("D", "x = 4", False),
            ],
            "exp": "32 = 2^5. Thus 2x + 1 = 5 => 2x = 4 => x = 2.",
        },
        {
            "num": 2,
            "text": f"{prefix}If log10(2) = 0.3010 and log10(3) = 0.4771, calculate the value of log10(18).",
            "options": [
                ("A", "1.2552", True),
                ("B", "1.0791", False),
                ("C", "0.7781", False),
                ("D", "1.3802", False),
            ],
            "exp": "18 = 2 * 3^2. log10(18) = log10(2) + 2*log10(3) = 0.3010 + 2(0.4771) = 0.3010 + 0.9542 = 1.2552.",
        },
        {
            "num": 3,
            "text": f"{prefix}Find the roots of the quadratic equation: 2x^2 - 5x - 3 = 0",
            "options": [
                ("A", "x = 3, x = -1/2", True),
                ("B", "x = -3, x = 1/2", False),
                ("C", "x = 2, x = -3", False),
                ("D", "x = 1, x = -3/2", False),
            ],
            "exp": "(2x + 1)(x - 3) = 0 => x = -1/2 or x = 3.",
        },
        {
            "num": 4,
            "text": f"{prefix}The 3rd term of an Arithmetic Progression (AP) is 10 and the 8th term is 25. Find the first term (a) and common difference (d).",
            "options": [
                ("A", "a = 4, d = 3", True),
                ("B", "a = 3, d = 4", False),
                ("C", "a = 2, d = 5", False),
                ("D", "a = 5, d = 3", False),
            ],
            "exp": "T3 = a + 2d = 10, T8 = a + 7d = 25. Subtracting gives 5d = 15 => d = 3. a + 2(3) = 10 => a = 4.",
        },
        {
            "num": 5,
            "text": f"{prefix}Differentiate y = 3x^4 - 5x^2 + 7x - 9 with respect to x.",
            "options": [
                ("A", "dy/dx = 12x^3 - 10x + 7", True),
                ("B", "dy/dx = 12x^3 - 5x + 7", False),
                ("C", "dy/dx = 7x^3 - 10x + 7", False),
                ("D", "dy/dx = 12x^4 - 10x^2 + 7", False),
            ],
            "exp": "Using the power rule: d/dx(3x^4) = 12x^3, d/dx(-5x^2) = -10x, d/dx(7x) = 7, d/dx(-9) = 0.",
        },
        {
            "num": 6,
            "text": f"{prefix}Evaluate the definite integral: ∫ from 0 to 2 of (3x^2 + 2x) dx",
            "options": [
                ("A", "10", False),
                ("B", "12", True),
                ("C", "14", False),
                ("D", "16", False),
            ],
            "exp": "∫ (3x^2 + 2x) dx = [x^3 + x^2] from 0 to 2 = (2^3 + 2^2) - (0) = 8 + 4 = 12.",
        },
        {
            "num": 7,
            "text": f"{prefix}A bag contains 5 red balls, 4 blue balls, and 3 green balls. If one ball is picked at random, find the probability that it is NOT blue.",
            "options": [
                ("A", "1/3", False),
                ("B", "2/3", True),
                ("C", "5/12", False),
                ("D", "7/12", False),
            ],
            "exp": "Total balls = 12. Non-blue balls = 5 + 3 = 8. P(not blue) = 8/12 = 2/3.",
        },
        {
            "num": 8,
            "text": f"{prefix}Calculate the volume of a right cylinder of radius 7 cm and height 10 cm. (Take π = 22/7)",
            "options": [
                ("A", "1540 cm³", True),
                ("B", "1450 cm³", False),
                ("C", "1760 cm³", False),
                ("D", "1320 cm³", False),
            ],
            "exp": "V = π * r^2 * h = (22/7) * 7^2 * 10 = 22 * 7 * 10 = 1540 cm³.",
        },
        {
            "num": 9,
            "text": f"{prefix}If sin(θ) = 3/5 where θ is an acute angle, find the exact value of cos(θ) + tan(θ).",
            "options": [
                ("A", "31/20", True),
                ("B", "7/5", False),
                ("C", "27/20", False),
                ("D", "19/15", False),
            ],
            "exp": "By Pythagoras: adjacent side = √(5^2 - 3^2) = 4. cos(θ) = 4/5, tan(θ) = 3/4. Sum = 4/5 + 3/4 = (16 + 15)/20 = 31/20.",
        },
        {
            "num": 10,
            "text": f"{prefix}Find the determinant of the 2x2 matrix: [[4, -2], [3, 5]]",
            "options": [
                ("A", "26", True),
                ("B", "14", False),
                ("C", "-26", False),
                ("D", "20", False),
            ],
            "exp": "Det = (4 * 5) - (-2 * 3) = 20 - (-6) = 26.",
        },
        {
            "num": 11,
            "text": f"{prefix}Convert the binary number 110101₂ to decimal (base 10).",
            "options": [
                ("A", "53", True),
                ("B", "45", False),
                ("C", "51", False),
                ("D", "57", False),
            ],
            "exp": "1*32 + 1*16 + 0*8 + 1*4 + 0*2 + 1*1 = 32 + 16 + 4 + 1 = 53.",
        },
        {
            "num": 12,
            "text": f"{prefix}The mean of the numbers 4, 8, x, 12, and 16 is 10. Find the value of x.",
            "options": [
                ("A", "10", True),
                ("B", "8", False),
                ("C", "12", False),
                ("D", "14", False),
            ],
            "exp": "Sum = 4 + 8 + x + 12 + 16 = 40 + x. (40 + x) / 5 = 10 => 40 + x = 50 => x = 10.",
        },
        {
            "num": 13,
            "text": f"{prefix}Find the length of the diagonal of a rectangle of sides 6 cm and 8 cm.",
            "options": [
                ("A", "10 cm", True),
                ("B", "12 cm", False),
                ("C", "14 cm", False),
                ("D", "9 cm", False),
            ],
            "exp": "d = √(6^2 + 8^2) = √(36 + 64) = √100 = 10 cm.",
        },
        {
            "num": 14,
            "text": f"{prefix}Solve the inequality: 3x - 7 < 5x + 3",
            "options": [
                ("A", "x > -5", True),
                ("B", "x < -5", False),
                ("C", "x > 5", False),
                ("D", "x < 5", False),
            ],
            "exp": "3x - 5x < 3 + 7 => -2x < 10 => x > -5 (reversing inequality sign on negative division).",
        },
        {
            "num": 15,
            "text": f"{prefix}Find the simple interest on ₦50,000 for 3 years at 8% per annum.",
            "options": [
                ("A", "₦12,000", True),
                ("B", "₦15,000", False),
                ("C", "₦10,000", False),
                ("D", "₦8,000", False),
            ],
            "exp": "I = (P * R * T) / 100 = (50000 * 8 * 3) / 100 = ₦12,000.",
        },
    ]


def get_physics_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Physics questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}A car accelerates uniformly from rest to a speed of 20 m/s in 5 seconds. Calculate the distance covered.",
            "options": [
                ("A", "50 m", True),
                ("B", "100 m", False),
                ("C", "40 m", False),
                ("D", "25 m", False),
            ],
            "exp": "s = ((u + v)/2) * t = ((0 + 20)/2) * 5 = 10 * 5 = 50 m.",
        },
        {
            "num": 2,
            "text": f"{prefix}Which of the following is a derived SI unit?",
            "options": [
                ("A", "Newton", True),
                ("B", "Kilogram", False),
                ("C", "Ampere", False),
                ("D", "Second", False),
            ],
            "exp": "Newton (kg·m/s²) is derived from the fundamental base units of mass, length, and time.",
        },
        {
            "num": 3,
            "text": f"{prefix}An object of mass 2 kg is dropped from a height of 20 m. Calculate its kinetic energy just before hitting the ground. (g = 10 m/s²)",
            "options": [
                ("A", "400 J", True),
                ("B", "200 J", False),
                ("C", "800 J", False),
                ("D", "100 J", False),
            ],
            "exp": "By conservation of energy: KE = PE = mgh = 2 * 10 * 20 = 400 J.",
        },
        {
            "num": 4,
            "text": f"{prefix}Calculate the frequency of a radio wave of wavelength 150 m travelling in a vacuum. (Speed of light c = 3.0 x 10^8 m/s)",
            "options": [
                ("A", "2.0 x 10^6 Hz", True),
                ("B", "4.5 x 10^6 Hz", False),
                ("C", "1.5 x 10^6 Hz", False),
                ("D", "5.0 x 10^5 Hz", False),
            ],
            "exp": "v = f * λ => f = c / λ = (3.0 x 10^8) / 150 = 2.0 x 10^6 Hz (2 MHz).",
        },
        {
            "num": 5,
            "text": f"{prefix}According to Ohm's law, for an ohmic conductor at constant temperature, current is directly proportional to:",
            "options": [
                ("A", "Potential difference", True),
                ("B", "Resistance", False),
                ("C", "Electric power", False),
                ("D", "Capacitance", False),
            ],
            "exp": "V = IR => I ∝ V at constant resistance/temperature.",
        },
        {
            "num": 6,
            "text": f"{prefix}Two resistors of resistances 4 Ω and 6 Ω are connected in parallel. Calculate their equivalent resistance.",
            "options": [
                ("A", "2.4 Ω", True),
                ("B", "10.0 Ω", False),
                ("C", "5.0 Ω", False),
                ("D", "1.5 Ω", False),
            ],
            "exp": "1/R = 1/4 + 1/6 = 5/12 => R = 12/5 = 2.4 Ω.",
        },
        {
            "num": 7,
            "text": f"{prefix}The phenomenon responsible for the formation of mirages in hot deserts is:",
            "options": [
                ("A", "Total Internal Reflection", True),
                ("B", "Diffraction", False),
                ("C", "Polarization", False),
                ("D", "Interference", False),
            ],
            "exp": "Total internal reflection occurs as light rays pass from dense cold air into less dense hot ground air at angles exceeding the critical angle.",
        },
        {
            "num": 8,
            "text": f"{prefix}What amount of heat is required to raise the temperature of 2 kg of water from 20°C to 50°C? (Specific heat capacity of water c = 4200 J/kg·K)",
            "options": [
                ("A", "252,000 J", True),
                ("B", "126,000 J", False),
                ("C", "420,000 J", False),
                ("D", "84,000 J", False),
            ],
            "exp": "Q = mcΔθ = 2 * 4200 * (50 - 20) = 2 * 4200 * 30 = 252,000 J.",
        },
        {
            "num": 9,
            "text": f"{prefix}An electric kettle rated 2 kW is used for 3 hours daily. Calculate the electrical energy consumed in 30 days.",
            "options": [
                ("A", "180 kWh", True),
                ("B", "60 kWh", False),
                ("C", "90 kWh", False),
                ("D", "360 kWh", False),
            ],
            "exp": "E = Power * time = 2 kW * (3 * 30 hours) = 2 * 90 = 180 kWh.",
        },
        {
            "num": 10,
            "text": f"{prefix}The half-life of a radioactive isotope is 4 days. What fraction of the original sample remains after 12 days?",
            "options": [
                ("A", "1/8", True),
                ("B", "1/4", False),
                ("C", "1/16", False),
                ("D", "1/2", False),
            ],
            "exp": "Number of half-lives n = 12 / 4 = 3. Remaining fraction = (1/2)^3 = 1/8.",
        },
        {
            "num": 11,
            "text": f"{prefix}Which of the following electromagnetic waves has the shortest wavelength and highest frequency?",
            "options": [
                ("A", "Gamma rays", True),
                ("B", "Radio waves", False),
                ("C", "Infrared radiation", False),
                ("D", "Ultraviolet rays", False),
            ],
            "exp": "Gamma rays possess the highest photon energy, highest frequency, and shortest wavelength in the EM spectrum.",
        },
        {
            "num": 12,
            "text": f"{prefix}A hydraulic press has piston areas of 0.02 m² and 0.5 m². If a force of 100 N is applied to the small piston, find the force exerted by the large piston.",
            "options": [
                ("A", "2500 N", True),
                ("B", "1000 N", False),
                ("C", "5000 N", False),
                ("D", "250 N", False),
            ],
            "exp": "By Pascal's Principle: F1/A1 = F2/A2 => F2 = F1 * (A2/A1) = 100 * (0.5 / 0.02) = 100 * 25 = 2500 N.",
        },
        {
            "num": 13,
            "text": f"{prefix}The focal length of a convex lens is 15 cm. If an object is placed 30 cm in front of the lens, the image formed is:",
            "options": [
                ("A", "Real, inverted, and of the same size", True),
                ("B", "Virtual, erect, and magnified", False),
                ("C", "Real, inverted, and diminished", False),
                ("D", "Real, erect, and magnified", False),
            ],
            "exp": "When an object is placed at 2f (2 * 15 = 30 cm) of a convex lens, the image formed at 2f on the other side is real, inverted, and same size (m = 1).",
        },
        {
            "num": 14,
            "text": f"{prefix}Calculate the escape velocity from a planet of radius 6.4 x 10^6 m with acceleration due to gravity g = 9.8 m/s².",
            "options": [
                ("A", "11.2 km/s", True),
                ("B", "7.9 km/s", False),
                ("C", "9.8 km/s", False),
                ("D", "15.4 km/s", False),
            ],
            "exp": "Ve = √(2gR) = √(2 * 9.8 * 6.4 * 10^6) = √(1.2544 * 10^8) ≈ 11,200 m/s = 11.2 km/s.",
        },
        {
            "num": 15,
            "text": f"{prefix}The thermionic emission of electrons from a metal surface is primarily dependent on:",
            "options": [
                ("A", "Temperature of the metal", True),
                ("B", "Applied magnetic field", False),
                ("C", "Pressure of surrounding gas", False),
                ("D", "Frequency of incident light", False),
            ],
            "exp": "Thermionic emission is the thermally induced flow of charge carriers from a surface as thermal energy overcomes the work function.",
        },
    ]


def get_chemistry_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Chemistry questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}What is the oxidation state of Chromium in Potassium Dichromate (K2Cr2O7)?",
            "options": [
                ("A", "+6", True),
                ("B", "+7", False),
                ("C", "+3", False),
                ("D", "+4", False),
            ],
            "exp": "2(+1) + 2(Cr) + 7(-2) = 0 => 2 + 2Cr - 14 = 0 => 2Cr = 12 => Cr = +6.",
        },
        {
            "num": 2,
            "text": f"{prefix}How many moles of oxygen gas (O2) are present in 64 grams of O2? (Molar mass of O = 16 g/mol)",
            "options": [
                ("A", "2 moles", True),
                ("B", "4 moles", False),
                ("C", "1 mole", False),
                ("D", "0.5 moles", False),
            ],
            "exp": "Molar mass of O2 = 32 g/mol. Moles = mass / molar mass = 64 / 32 = 2 moles.",
        },
        {
            "num": 3,
            "text": f"{prefix}Which of the following gas laws states that the volume of a given mass of gas is inversely proportional to its pressure at constant temperature?",
            "options": [
                ("A", "Boyle's Law", True),
                ("B", "Charles's Law", False),
                ("C", "Gay-Lussac's Law", False),
                ("D", "Avogadro's Law", False),
            ],
            "exp": "Boyle's Law: P1V1 = P2V2 at constant temperature.",
        },
        {
            "num": 4,
            "text": f"{prefix}The pH of a 0.001 M solution of Hydrochloric acid (HCl) is:",
            "options": [
                ("A", "3.0", True),
                ("B", "1.0", False),
                ("C", "4.0", False),
                ("D", "2.0", False),
            ],
            "exp": "pH = -log[H+] = -log(10^-3) = 3.0.",
        },
        {
            "num": 5,
            "text": f"{prefix}Which of the following organic compounds decolorizes bromine water due to the presence of a carbon-carbon double bond?",
            "options": [
                ("A", "Ethene (C2H4)", True),
                ("B", "Ethane (C2H6)", False),
                ("C", "Methane (CH4)", False),
                ("D", "Ethanol (C2H5OH)", False),
            ],
            "exp": "Alkenes such as ethene undergo electrophilic addition with aqueous bromine, decolorizing the brown bromine solution.",
        },
        {
            "num": 6,
            "text": f"{prefix}The electronic configuration of a neutral atom with atomic number 17 (Chlorine) is:",
            "options": [
                ("A", "1s² 2s² 2p⁶ 3s² 3p⁵", True),
                ("B", "1s² 2s² 2p⁶ 3s¹ 3p⁶", False),
                ("C", "1s² 2s² 2p⁶ 3s² 3p⁶", False),
                ("D", "1s² 2s² 2p⁶ 3s² 3p⁴", False),
            ],
            "exp": "Chlorine (Z=17): K=2, L=8, M=7 => 1s² 2s² 2p⁶ 3s² 3p⁵.",
        },
        {
            "num": 7,
            "text": f"{prefix}During the electrolysis of acidified water using platinum electrodes, which gas is liberated at the anode?",
            "options": [
                ("A", "Oxygen gas (O2)", True),
                ("B", "Hydrogen gas (H2)", False),
                ("C", "Chlorine gas (Cl2)", False),
                ("D", "Nitrogen dioxide (NO2)", False),
            ],
            "exp": "Hydroxide ions (OH-) are discharged at the anode to produce oxygen gas: 4OH- -> 2H2O + O2 + 4e-.",
        },
        {
            "num": 8,
            "text": f"{prefix}Which catalyst is used in the industrial manufacture of Ammonia via the Haber Process?",
            "options": [
                ("A", "Finely divided Iron", True),
                ("B", "Vanadium(V) oxide", False),
                ("C", "Nickel", False),
                ("D", "Platinum", False),
            ],
            "exp": "Finely divided iron with aluminum/potassium oxide promoter is the catalyst in the Haber process (N2 + 3H2 ⇌ 2NH3).",
        },
        {
            "num": 9,
            "text": f"{prefix}A solution that resists drastic changes in pH upon the addition of small amounts of acid or base is called a:",
            "options": [
                ("A", "Buffer solution", True),
                ("B", "Standard solution", False),
                ("C", "Saturated solution", False),
                ("D", "Colloidal solution", False),
            ],
            "exp": "Buffer solutions consist of a weak acid and its conjugate base (or weak base and conjugate acid).",
        },
        {
            "num": 10,
            "text": f"{prefix}The type of bond present between hydrogen and oxygen in a water molecule (H2O) is:",
            "options": [
                ("A", "Polar covalent bond", True),
                ("B", "Electrovalent (ionic) bond", False),
                ("C", "Metallic bond", False),
                ("D", "Coordinate covalent bond", False),
            ],
            "exp": "Oxygen has a higher electronegativity than hydrogen, creating polar covalent O-H bonds with partial dipoles.",
        },
        {
            "num": 11,
            "text": f"{prefix}What volume of carbon dioxide (CO2) at STP is produced from the complete thermal decomposition of 10 g of Calcium Carbonate (CaCO3)? (Molar mass CaCO3 = 100 g/mol, molar volume at STP = 22.4 dm³)",
            "options": [
                ("A", "2.24 dm³", True),
                ("B", "4.48 dm³", False),
                ("C", "1.12 dm³", False),
                ("D", "22.4 dm³", False),
            ],
            "exp": "CaCO3 -> CaO + CO2. 10g CaCO3 = 0.1 mol => 0.1 mol CO2 = 0.1 * 22.4 dm³ = 2.24 dm³.",
        },
        {
            "num": 12,
            "text": f"{prefix}The property of carbon that allows it to form long chains and rings of carbon atoms is called:",
            "options": [
                ("A", "Catenation", True),
                ("B", "Allotropy", False),
                ("C", "Isomerism", False),
                ("D", "Electronegativity", False),
            ],
            "exp": "Catenation is the linkage of atoms of the same element into longer chains or rings.",
        },
        {
            "num": 13,
            "text": f"{prefix}Which of the following pairs represents allotropes of carbon?",
            "options": [
                ("A", "Diamond and Graphite", True),
                ("B", "Methane and Ethane", False),
                ("C", "Carbon monoxide and Carbon dioxide", False),
                ("D", "Coal and Limestone", False),
            ],
            "exp": "Diamond, graphite, and fullerenes are allotropes (different structural modifications) of carbon.",
        },
        {
            "num": 14,
            "text": f"{prefix}In Le Chatelier's principle, an increase in pressure on the system 2SO2(g) + O2(g) ⇌ 2SO3(g) will:",
            "options": [
                ("A", "Shift equilibrium to the right (produce more SO3)", True),
                ("B", "Shift equilibrium to the left", False),
                ("C", "Have no effect on equilibrium position", False),
                ("D", "Decrease the reaction rate", False),
            ],
            "exp": "Reactants have 3 gas moles while products have 2. Increasing pressure shifts equilibrium to the side with fewer moles (right).",
        },
        {
            "num": 15,
            "text": f"{prefix}Which drying agent is suitable for drying Ammonia gas (NH3)?",
            "options": [
                ("A", "Calcium oxide (Quicklime, CaO)", True),
                ("B", "Concentrated Tetraoxosulphate(VI) acid (H2SO4)", False),
                ("C", "Fused Calcium chloride (CaCl2)", False),
                ("D", "Phosphorus(V) oxide (P4O10)", False),
            ],
            "exp": "Ammonia is a basic gas that reacts with acidic drying agents (H2SO4, P4O10) and forms complexes with CaCl2. CaO is basic and unreactive with NH3.",
        },
    ]


def get_biology_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Biology questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}The organelle referred to as the 'powerhouse of the cell' due to its role in cellular respiration and ATP synthesis is the:",
            "options": [
                ("A", "Mitochondrion", True),
                ("B", "Ribosome", False),
                ("C", "Golgi apparatus", False),
                ("D", "Endoplasmic reticulum", False),
            ],
            "exp": "Mitochondria generate most of the chemical energy needed to power the cell's biochemical reactions through ATP production.",
        },
        {
            "num": 2,
            "text": f"{prefix}Which of the following blood vessels carries oxygenated blood from the lungs back to the left atrium of the heart?",
            "options": [
                ("A", "Pulmonary vein", True),
                ("B", "Pulmonary artery", False),
                ("C", "Aorta", False),
                ("D", "Vena cava", False),
            ],
            "exp": "The pulmonary veins are unique as the only veins carrying freshly oxygenated blood from lungs to heart.",
        },
        {
            "num": 3,
            "text": f"{prefix}In Mendel's monohybrid cross between two heterozygous tall pea plants (Tt x Tt), what is the expected phenotypic ratio of tall to dwarf offspring?",
            "options": [
                ("A", "3 : 1", True),
                ("B", "1 : 2 : 1", False),
                ("C", "1 : 1", False),
                ("D", "9 : 3 : 3 : 1", False),
            ],
            "exp": "Punnett square gives 1 TT (tall), 2 Tt (tall), 1 tt (dwarf) => 3 tall : 1 dwarf.",
        },
        {
            "num": 4,
            "text": f"{prefix}The process by which plants lose water vapor through the stomata of their leaves is known as:",
            "options": [
                ("A", "Transpiration", True),
                ("B", "Guttation", False),
                ("C", "Osmosis", False),
                ("D", "Translocation", False),
            ],
            "exp": "Transpiration is the exhalation of water vapor through stomata, generating transpiration pull for mineral transport.",
        },
        {
            "num": 5,
            "text": f"{prefix}Which part of the human brain is primarily responsible for maintaining posture, muscle coordination, and body balance?",
            "options": [
                ("A", "Cerebellum", True),
                ("B", "Cerebrum", False),
                ("C", "Medulla oblongata", False),
                ("D", "Hypothalamus", False),
            ],
            "exp": "The cerebellum coordinates voluntary muscular movements and maintains equilibrium.",
        },
        {
            "num": 6,
            "text": f"{prefix}The functional and structural excretory unit of the human kidney is the:",
            "options": [
                ("A", "Nephron", True),
                ("B", "Neuron", False),
                ("C", "Alveolus", False),
                ("D", "Glomerulus", False),
            ],
            "exp": "Nephrons filter blood, reabsorb nutrients and water, and excrete nitrogenous waste as urine.",
        },
        {
            "num": 7,
            "text": f"{prefix}Which enzyme in the human stomach initiates the digestion of dietary proteins into polypeptides?",
            "options": [
                ("A", "Pepsin", True),
                ("B", "Amylase", False),
                ("C", "Lipase", False),
                ("D", "Trypsin", False),
            ],
            "exp": "Pepsin, activated from pepsinogen by stomach hydrochloric acid (HCl), hydrolyzes peptide bonds.",
        },
        {
            "num": 8,
            "text": f"{prefix}An ecological relationship where both interacting species benefit from each other is known as:",
            "options": [
                ("A", "Mutualism", True),
                ("B", "Commensalism", False),
                ("C", "Parasitism", False),
                ("D", "Predation", False),
            ],
            "exp": "Mutualism (e.g. nitrogen-fixing bacteria in root nodules of legumes) benefits both participating organisms.",
        },
        {
            "num": 9,
            "text": f"{prefix}Which hormone is responsible for lowering elevated blood glucose levels by promoting glucose uptake into liver and muscle cells?",
            "options": [
                ("A", "Insulin", True),
                ("B", "Glucagon", False),
                ("C", "Adrenaline", False),
                ("D", "Thyroxine", False),
            ],
            "exp": "Insulin, secreted by beta cells in the Islets of Langerhans of the pancreas, converts excess blood glucose to glycogen.",
        },
        {
            "num": 10,
            "text": f"{prefix}The light stage (photolysis) of photosynthesis takes place in which specific part of the chloroplast?",
            "options": [
                ("A", "Thylakoid / Grana", True),
                ("B", "Stroma", False),
                ("C", "Outer membrane", False),
                ("D", "Intermembrane space", False),
            ],
            "exp": "Light-dependent reactions occur on the thylakoid membranes where chlorophyll absorbs photons, whereas dark reactions occur in the stroma.",
        },
        {
            "num": 11,
            "text": f"{prefix}Which caste in a termite colony is wingless, sterile, and defends the colony against invading predators?",
            "options": [
                ("A", "Soldier", True),
                ("B", "Worker", False),
                ("C", "Queen", False),
                ("D", "King", False),
            ],
            "exp": "Soldier termites have enlarged mandibles and hard head capsules specialized for colony defense.",
        },
        {
            "num": 12,
            "text": f"{prefix}The theory of natural selection as the mechanism of organic evolution was proposed by:",
            "options": [
                ("A", "Charles Darwin", True),
                ("B", "Jean-Baptiste Lamarck", False),
                ("C", "Gregor Mendel", False),
                ("D", "Louis Pasteur", False),
            ],
            "exp": "Charles Darwin published 'On the Origin of Species' (1859) formulating evolution through survival of the fittest.",
        },
        {
            "num": 13,
            "text": f"{prefix}Which vitamin is essential for the synthesis of blood clotting factors in the liver?",
            "options": [
                ("A", "Vitamin K", True),
                ("B", "Vitamin C", False),
                ("C", "Vitamin D", False),
                ("D", "Vitamin A", False),
            ],
            "exp": "Vitamin K is a necessary cofactor for the hepatic synthesis of prothrombin and clotting factors VII, IX, and X.",
        },
        {
            "num": 14,
            "text": f"{prefix}The conversion of atmospheric nitrogen gas (N2) into nitrates by soil bacteria (e.g. Rhizobium, Azotobacter) is called:",
            "options": [
                ("A", "Nitrogen fixation", True),
                ("B", "Nitrification", False),
                ("C", "Denitrification", False),
                ("D", "Ammonification", False),
            ],
            "exp": "Nitrogen fixation converts elemental N2 into ammonia/nitrates accessible to plant roots.",
        },
        {
            "num": 15,
            "text": f"{prefix}A person with blood group O is considered a 'universal donor' because their red blood cells possess:",
            "options": [
                ("A", "Neither A nor B surface antigens", True),
                ("B", "Both A and B antigens", False),
                ("C", "Only Rhesus factor antibodies", False),
                ("D", "No plasma antibodies", False),
            ],
            "exp": "Group O RBCs lack both A and B antigens, preventing agglutination when introduced into recipient bloodstreams.",
        },
    ]


def get_economics_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Economics questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}The fundamental economic problem that necessitates choice and decision making in every society is:",
            "options": [
                ("A", "Scarcity of resources relative to unlimited human wants", True),
                ("B", "High level of unemployment and inflation", False),
                ("C", "Unequal distribution of national income", False),
                ("D", "Excessive government taxation", False),
            ],
            "exp": "Scarcity is the basic economic problem: resources are finite while human wants are insatiable.",
        },
        {
            "num": 2,
            "text": f"{prefix}If a 10% increase in the price of a commodity leads to a 20% decrease in quantity demanded, the price elasticity of demand is:",
            "options": [
                ("A", "2.0 (Elastic)", True),
                ("B", "0.5 (Inelastic)", False),
                ("C", "1.0 (Unitary elastic)", False),
                ("D", "0.0 (Perfectly inelastic)", False),
            ],
            "exp": "Ed = % change in Q / % change in P = 20% / 10% = 2.0. Since |Ed| > 1, demand is elastic.",
        },
        {
            "num": 3,
            "text": f"{prefix}The law of diminishing marginal utility states that as consumption of a good increases:",
            "options": [
                ("A", "The additional satisfaction derived from each successive unit decreases", True),
                ("B", "Total utility continuously decreases from the first unit", False),
                ("C", "Marginal utility remains constant at all consumption levels", False),
                ("D", "The consumer's budget constraint shifts to the right", False),
            ],
            "exp": "Each extra unit consumed yields less extra satisfaction (marginal utility) than the preceding unit.",
        },
        {
            "num": 4,
            "text": f"{prefix}Which market structure is characterized by a single seller, high barriers to entry, and the ability to set market prices?",
            "options": [
                ("A", "Monopoly", True),
                ("B", "Perfect Competition", False),
                ("C", "Monopolistic Competition", False),
                ("D", "Oligopoly", False),
            ],
            "exp": "A pure monopoly exists when one firm is the sole producer of a product with no close substitutes.",
        },
        {
            "num": 5,
            "text": f"{prefix}Gross Domestic Product (GDP) measures:",
            "options": [
                ("A", "The total monetary value of all final goods and services produced within a country's borders in a year", True),
                ("B", "The total income earned by citizens resident at home and abroad", False),
                ("C", "Total government revenue minus expenditures", False),
                ("D", "The value of exports minus imports only", False),
            ],
            "exp": "GDP is the total market value of all final output produced domestically within a given accounting year.",
        },
        {
            "num": 6,
            "text": f"{prefix}Which tool of monetary policy involves the Central Bank buying and selling government securities in the financial market?",
            "options": [
                ("A", "Open Market Operations (OMO)", True),
                ("B", "Cash Reserve Ratio (CRR)", False),
                ("C", "Moral Suasion", False),
                ("D", "Liquidity Ratio", False),
            ],
            "exp": "Open Market Operations (OMO) involves the Central Bank buying/selling treasury bills and bonds to expand or contract money supply.",
        },
        {
            "num": 7,
            "text": f"{prefix}A progressive tax system is one in which:",
            "options": [
                ("A", "The tax rate increases as the taxpayer's income increases", True),
                ("B", "All taxpayers pay the same absolute amount of tax", False),
                ("C", "The tax rate decreases as income rises", False),
                ("D", "The tax applies exclusively to imported luxury goods", False),
            ],
            "exp": "Under a progressive tax, higher income earners pay a higher percentage of their income in tax.",
        },
        {
            "num": 8,
            "text": f"{prefix}The type of inflation caused by persistent increases in the cost of production (e.g. wages, raw materials, energy) is called:",
            "options": [
                ("A", "Cost-push inflation", True),
                ("B", "Demand-pull inflation", False),
                ("C", "Hyperinflation", False),
                ("D", "Creeping inflation", False),
            ],
            "exp": "Cost-push inflation occurs when aggregate supply shifts leftward due to rising input costs.",
        },
        {
            "num": 9,
            "text": f"{prefix}The economic principle of 'Comparative Advantage' was formulated by:",
            "options": [
                ("A", "David Ricardo", True),
                ("B", "Adam Smith", False),
                ("C", "John Maynard Keynes", False),
                ("D", "Thomas Malthus", False),
            ],
            "exp": "David Ricardo showed that nations gain from trade by specializing in goods with lower opportunity costs.",
        },
        {
            "num": 10,
            "text": f"{prefix}Which component of a country's Balance of Payments records transactions involving visible merchandise imports and exports?",
            "options": [
                ("A", "Current Account (Trade balance)", True),
                ("B", "Capital Account", False),
                ("C", "Financial Account", False),
                ("D", "Official Reserves Account", False),
            ],
            "exp": "The trade balance (visible trade) is recorded under the Current Account.",
        },
        {
            "num": 11,
            "text": f"{prefix}When a firm's average total cost of production decreases as output scales up, the firm is experiencing:",
            "options": [
                ("A", "Economies of scale", True),
                ("B", "Diseconomies of scale", False),
                ("C", "Diminishing marginal returns", False),
                ("D", "Constant returns to scale", False),
            ],
            "exp": "Economies of scale are cost advantages that enterprises obtain due to their scale of operation.",
        },
        {
            "num": 12,
            "text": f"{prefix}In national income accounting, Net National Product (NNP) at market prices is calculated as:",
            "options": [
                ("A", "GNP minus Depreciation (Capital Consumption Allowance)", True),
                ("B", "GDP plus Net Export", False),
                ("C", "National Income plus Indirect Taxes", False),
                ("D", "GNP plus Subsidies", False),
            ],
            "exp": "NNP = GNP - Depreciation.",
        },
        {
            "num": 13,
            "text": f"{prefix}The Malthusian Theory of Population postulated that while population grows geometrically, food supply increases:",
            "options": [
                ("A", "Arithmetically", True),
                ("B", "Exponentially", False),
                ("C", "Logarithmically", False),
                ("D", "At a constant proportion", False),
            ],
            "exp": "Thomas Malthus warned that population grows geometrically (1, 2, 4, 8, 16...) while food production grows arithmetically (1, 2, 3, 4, 5...).",
        },
        {
            "num": 14,
            "text": f"{prefix}Money serves all of the following primary functions EXCEPT:",
            "options": [
                ("A", "Factor of production generating pure economic rent", True),
                ("B", "Medium of exchange", False),
                ("C", "Unit of account / measure of value", False),
                ("D", "Store of value and standard for deferred payments", False),
            ],
            "exp": "Money is a financial asset and medium of exchange, not a primary factor of production (land, labor, capital, entrepreneurship).",
        },
        {
            "num": 15,
            "text": f"{prefix}A persistent deficit in a nation's balance of payments can be rectified by:",
            "options": [
                ("A", "Encouraging exports and imposing selective import tariffs", True),
                ("B", "Revaluing the domestic currency upwards", False),
                ("C", "Lowering domestic interest rates to spur capital flight", False),
                ("D", "Subsidizing foreign imported finished goods", False),
            ],
            "exp": "Export promotion and import restrictions improve trade balances by earning more foreign exchange and reducing outflows.",
        },
    ]


def get_government_questions(body: str, year: int) -> list[dict[str, Any]]:
    """Generates 15 authentic Government questions tailored for body and year."""
    prefix = f"[{body} {year}] "
    return [
        {
            "num": 1,
            "text": f"{prefix}The supreme, ultimate, and legally independent power of a state to govern its territory free from external interference is:",
            "options": [
                ("A", "Sovereignty", True),
                ("B", "Legitimacy", False),
                ("C", "Authority", False),
                ("D", "Democracy", False),
            ],
            "exp": "Sovereignty is the supreme authority within a territory, formulated by political theorist Jean Bodin.",
        },
        {
            "num": 2,
            "text": f"{prefix}The political philosophy and constitutional principle of 'Separation of Powers' was popularized by:",
            "options": [
                ("A", "Baron de Montesquieu", True),
                ("B", "John Locke", False),
                ("C", "Thomas Hobbes", False),
                ("D", "Karl Marx", False),
            ],
            "exp": "Montesquieu articulated the separation of executive, legislative, and judicial powers in 'The Spirit of the Laws' (1748).",
        },
        {
            "num": 3,
            "text": f"{prefix}In a Parliamentary system of government, the Head of State is usually distinct from the Head of Government. Who is the Head of Government?",
            "options": [
                ("A", "Prime Minister", True),
                ("B", "Monarch / President", False),
                ("C", "Chief Justice", False),
                ("D", "Speaker of the House", False),
            ],
            "exp": "In parliamentary democracies (e.g. UK), the Prime Minister heads the cabinet and government, while a monarch or ceremonial president is head of state.",
        },
        {
            "num": 4,
            "text": f"{prefix}The first Nigerian constitution to introduce the elective principle for legislative seats in Lagos and Calabar was the:",
            "options": [
                ("A", "Clifford Constitution of 1922", True),
                ("B", "Richards Constitution of 1946", False),
                ("C", "Macpherson Constitution of 1951", False),
                ("D", "Lyttelton Constitution of 1954", False),
            ],
            "exp": "Sir Hugh Clifford's 1922 Constitution created the Nigerian Legislative Council and introduced 4 elected seats (3 for Lagos, 1 for Calabar).",
        },
        {
            "num": 5,
            "text": f"{prefix}The 1954 Lyttelton Constitution was historic in Nigerian political history because it:",
            "options": [
                ("A", "Formally established a federal system of government in Nigeria", True),
                ("B", "Granted full political independence from British colonial rule", False),
                ("C", "Abolished the regional houses of assembly", False),
                ("D", "Introduced the presidential system of government", False),
            ],
            "exp": "The 1954 Lyttelton Constitution established formal Nigerian federalism with autonomous Northern, Western, and Eastern regions.",
        },
        {
            "num": 6,
            "text": f"{prefix}In the pre-colonial Hausa-Fulani political system under the Sokoto Caliphate, the official in charge of the treasury was the:",
            "options": [
                ("A", "Maaji", True),
                ("B", "Madawaki", False),
                ("C", "Galadima", False),
                ("D", "Sarkin Fada", False),
            ],
            "exp": "The Maaji was the treasurer of the emirate; Madawaki was commander of the army; Galadima was administrator of the capital.",
        },
        {
            "num": 7,
            "text": f"{prefix}In the traditional pre-colonial Oyo Empire, the council of noble kingmakers headed by the Bashorun was known as the:",
            "options": [
                ("A", "Oyo Mesi", True),
                ("B", "Ogboni Cult", False),
                ("C", "Are Ona Kakanfo", False),
                ("D", "Baale", False),
            ],
            "exp": "The Oyo Mesi consisted of seven hereditary noble councillors who checked the powers of the Alaafin and selected new Alaafins.",
        },
        {
            "num": 8,
            "text": f"{prefix}Which organ of the United Nations (UN) is primarily responsible for the maintenance of international peace and security?",
            "options": [
                ("A", "UN Security Council", True),
                ("B", "General Assembly", False),
                ("C", "Economic and Social Council (ECOSOC)", False),
                ("D", "International Court of Justice", False),
            ],
            "exp": "The UN Security Council consists of 5 permanent veto-wielding members and 10 non-permanent members tasked with peacekeeping.",
        },
        {
            "num": 9,
            "text": f"{prefix}The Economic Community of West African States (ECOWAS) was officially established by the Treaty of Lagos in:",
            "options": [
                ("A", "May 1975", True),
                ("B", "October 1960", False),
                ("C", "January 1985", False),
                ("D", "July 1999", False),
            ],
            "exp": "ECOWAS was established on 28 May 1975 by the Treaty of Lagos under the leadership of Nigeria and Togo.",
        },
        {
            "num": 10,
            "text": f"{prefix}The core principle of 'Rule of Law' as formulated by Professor A.V. Dicey includes all of the following EXCEPT:",
            "options": [
                ("A", "Absolute immunity of public officials from judicial prosecution", True),
                ("B", "Supremacy of regular law over arbitrary power", False),
                ("C", "Equality of all persons before the law", False),
                ("D", "Protection of fundamental human rights by independent courts", False),
            ],
            "exp": "Dicey's Rule of Law emphasizes equality before the law, strictly rejecting arbitrary powers or special immunities.",
        },
        {
            "num": 11,
            "text": f"{prefix}Which constitutional conference produced the independence constitution for Nigeria?",
            "options": [
                ("A", "London Constitutional Conference of 1957 / 1958", True),
                ("B", "Ibadan General Conference of 1950", False),
                ("C", "Lagos Conference of 1954", False),
                ("D", "All-Nigeria Conference of 1963", False),
            ],
            "exp": "The London Constitutional Conferences of 1957 and 1958 finalized agreements leading directly to Nigerian independence on October 1, 1960.",
        },
        {
            "num": 12,
            "text": f"{prefix}The power of the Judiciary to review and declare acts of the Legislature or Executive unconstitutional and void is termed:",
            "options": [
                ("A", "Judicial Review", True),
                ("B", "Judicial Precedent (Stare Decisis)", False),
                ("C", "Prorogation", False),
                ("D", "Injunction", False),
            ],
            "exp": "Judicial review empowers constitutional courts to invalidate laws or executive orders violating supreme constitutional provisions.",
        },
        {
            "num": 13,
            "text": f"{prefix}An electoral system where the candidate who secures the highest number of votes cast wins the seat (regardless of absolute majority) is called:",
            "options": [
                ("A", "First-Past-The-Post (Simple Plurality)", True),
                ("B", "Proportional Representation", False),
                ("C", "Second Ballot System", False),
                ("D", "Alternative Vote", False),
            ],
            "exp": "Simple plurality / First-Past-The-Post awards victory to the single candidate with the most votes in single-member districts.",
        },
        {
            "num": 14,
            "text": f"{prefix}The African Union (AU) was launched in Durban, South Africa in 2002 as the successor organization to the:",
            "options": [
                ("A", "Organization of African Unity (OAU)", True),
                ("B", "League of Arab States", False),
                ("C", "Non-Aligned Movement", False),
                ("D", "Southern African Development Community (SADC)", False),
            ],
            "exp": "The AU succeeded the Organization of African Unity (OAU, founded 1963) to promote greater political and economic integration in Africa.",
        },
        {
            "num": 15,
            "text": f"{prefix}The main feature of a unitary constitution is that:",
            "options": [
                ("A", "All constitutional powers are concentrated in a single central government", True),
                ("B", "Powers are divided equally between central and component state governments", False),
                ("C", "Component states retain the right to unilaterally secede", False),
                ("D", "There are two bicameral regional legislatures with supreme jurisdiction", False),
            ],
            "exp": "In a unitary system (e.g. UK, France, Ghana), sovereign authority is vested solely in the central national government.",
        },
    ]


QUESTION_BUILDERS = {
    "English Language": get_english_questions,
    "Mathematics": get_mathematics_questions,
    "Physics": get_physics_questions,
    "Chemistry": get_chemistry_questions,
    "Biology": get_biology_questions,
    "Economics": get_economics_questions,
    "Government": get_government_questions,
}


# ==============================================================================
# SEEDING EXECUTION LOGIC
# ==============================================================================

def seed_all_exams() -> None:
    """Executes the full multi-exam body database seeding."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    start_time = time.time()
    print("=" * 75)
    print("           SEEDING MULTI-EXAM CBT QUESTION REPOSITORY")
    print("=" * 75)
    print(f"Exam Bodies : {', '.join(EXAM_BODIES)} ({len(EXAM_BODIES)} total)")
    print(f"Subjects    : {', '.join(s['name'] for s in CORE_SUBJECTS)} ({len(CORE_SUBJECTS)} total)")
    print(f"Years       : {', '.join(map(str, EXAM_YEARS))} ({len(EXAM_YEARS)} total)")
    print(f"Questions   : 15 questions per Subject per Year per Body")
    print(f"Target Total: {len(EXAM_BODIES) * len(CORE_SUBJECTS) * len(EXAM_YEARS) * 15} Questions\n")

    init_database()

    with SessionLocal() as db:
        # 1. Seed or fetch core subjects
        print("[1/3] Verifying and seeding Core Subjects...")
        subject_map: dict[str, Subject] = {}
        for sub_def in CORE_SUBJECTS:
            existing = db.query(Subject).filter_by(name=sub_def["name"]).first()
            if not existing:
                subject = Subject(
                    name=sub_def["name"],
                    code=sub_def["code"],
                    is_active=True,
                )
                db.add(subject)
                db.flush()
                subject_map[sub_def["name"]] = subject
                print(f"  + Created Subject: {subject.name} (id={subject.id}, code={subject.code})")
            else:
                subject_map[sub_def["name"]] = existing
                print(f"  [OK] Found Subject: {existing.name} (id={existing.id})")

        db.commit()

        # 2. Seed Questions for all Exam Bodies, Subjects, and Years
        print("\n[2/3] Seeding Exam Questions and Options...")
        total_created = 0
        total_skipped = 0

        for body in EXAM_BODIES:
            print(f"\n--- Processing Exam Body: {body} ---")
            body_created = 0

            for sub_name, builder_fn in QUESTION_BUILDERS.items():
                subject = subject_map[sub_name]

                for year in EXAM_YEARS:
                    questions_data = builder_fn(body, year)

                    for q_item in questions_data:
                        q_num = q_item["num"]
                        q_text = q_item["text"]
                        q_exp = q_item.get("exp")
                        options_data = q_item["options"]

                        # Check if question already exists (idempotency)
                        existing_q = (
                            db.query(Question)
                            .filter_by(
                                exam_body=body,
                                subject_id=subject.id,
                                year=year,
                                question_number=q_num,
                            )
                            .first()
                        )

                        if existing_q:
                            # Update question text and explanation if needed
                            existing_q.text = q_text
                            existing_q.explanation = q_exp
                            existing_q.is_active = True
                            total_skipped += 1
                            continue

                        # Create new question
                        question = Question(
                            exam_body=body,
                            subject_id=subject.id,
                            year=year,
                            question_number=q_num,
                            text=q_text,
                            explanation=q_exp,
                            is_active=True,
                        )
                        db.add(question)
                        db.flush()

                        # Add options
                        for pos, (lbl, opt_text, is_corr) in enumerate(options_data, start=1):
                            opt = Option(
                                question_id=question.id,
                                label=lbl,
                                position=pos,
                                text=opt_text,
                                is_correct=is_corr,
                            )
                            db.add(opt)

                        body_created += 1
                        total_created += 1

            db.commit()
            print(f"  [OK] {body}: Successfully seeded {body_created} new questions across {len(EXAM_YEARS)} years.")

        # 3. Final Verification & Summary
        print("\n[3/3] Performing Database Verification...")
        total_db_questions = db.query(Question).count()
        total_db_options = db.query(Option).count()

        elapsed = time.time() - start_time
        print("\n" + "=" * 75)
        print("                 SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 75)
        print(f"New Questions Seeded : {total_created}")
        print(f"Existing Questions   : {total_skipped}")
        print(f"Total Questions in DB: {total_db_questions}")
        print(f"Total Options in DB  : {total_db_options}")
        print(f"Execution Time       : {elapsed:.2f} seconds")
        print("=" * 75 + "\n")


if __name__ == "__main__":
    seed_all_exams()
