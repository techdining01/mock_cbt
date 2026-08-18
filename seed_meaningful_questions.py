"""
Seed Script: Realistic CBT Examination Question Bank
Seeds 10+ core secondary school subjects across 3 class levels (SS1/2022, SS2/2023, SS3/2024),
with 5 curated, curriculum-accurate academic questions per subject per class.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.database import SessionLocal, init_database
from app.database.models import Option, Question, Subject, User

# ==============================================================================
# SEED DATA DEFINITION
# ==============================================================================

SUBJECTS_DATA = [
    {"name": "English Language", "code": "ENG"},
    {"name": "Mathematics", "code": "MTH"},
    {"name": "Physics", "code": "PHY"},
    {"name": "Chemistry", "code": "CHM"},
    {"name": "Biology", "code": "BIO"},
    {"name": "Economics", "code": "ECO"},
    {"name": "Government", "code": "GOV"},
    {"name": "Literature in English", "code": "LIT"},
    {"name": "Commerce", "code": "COM"},
    {"name": "Agricultural Science", "code": "AGR"},
    {"name": "Computer Studies", "code": "CMP"},
    {"name": "Civic Education", "code": "CIV"},
]

STUDENTS_DATA = [
    # SS1 Class
    {
        "username": "zainab.ali",
        "full_name": "Zainab Ali",
        "role": "student",
        "student_class": "SS1 Gold",
        "admission_year": 2024,
    },
    {
        "username": "tobi.ade",
        "full_name": "Tobi Adebayo",
        "role": "student",
        "student_class": "SS1 Silver",
        "admission_year": 2024,
    },
    # SS2 Class
    {
        "username": "emeka.nwosu",
        "full_name": "Emeka Nwosu",
        "role": "student",
        "student_class": "SS2 Diamond",
        "admission_year": 2023,
    },
    {
        "username": "amara.kalu",
        "full_name": "Amarachi Kalu",
        "role": "student",
        "student_class": "SS2 Ruby",
        "admission_year": 2023,
    },
    # SS3 Class
    {
        "username": "blessing.adams",
        "full_name": "Blessing Adams",
        "role": "student",
        "student_class": "SS3 Emerald",
        "admission_year": 2022,
    },
    {
        "username": "farouk.umar",
        "full_name": "Farouk Umar",
        "role": "student",
        "student_class": "SS3 Gold",
        "admission_year": 2022,
    },
]

# Structure: {Subject_Name: {Year/Class: [5 Questions]}}
# Years represent Class Tiers: 2022 = SS1, 2023 = SS2, 2024 = SS3
QUESTIONS_BANK = {
    "English Language": {
        2022: [  # SS1 Level
            {
                "num": 1,
                "text": "Choose the word nearest in meaning to the underlined word:\nThe manager gave a METICULOUS account of the company's annual expenses.",
                "explanation": "'Meticulous' means showing great attention to detail; very careful and precise.",
                "options": [
                    ("A", "careless", False),
                    ("B", "painstaking", True),
                    ("C", "hasty", False),
                    ("D", "brief", False),
                    ("E", "confusing", False),
                ],
            },
            {
                "num": 2,
                "text": "Identify the figure of speech in the sentence: 'The wind whispered through the dark pines.'",
                "explanation": "Personification is the attribution of human characteristics or qualities to non-human things.",
                "options": [
                    ("A", "Metaphor", False),
                    ("B", "Simile", False),
                    ("C", "Personification", True),
                    ("D", "Hyperbole", False),
                    ("E", "Irony", False),
                ],
            },
            {
                "num": 3,
                "text": "Choose the correct preposition to fill the blank: 'She is capable ______ handling complex financial reports.'",
                "explanation": "The adjective 'capable' is consistently followed by the preposition 'of'.",
                "options": [
                    ("A", "at", False),
                    ("B", "for", False),
                    ("C", "of", True),
                    ("D", "with", False),
                    ("E", "in", False),
                ],
            },
            {
                "num": 4,
                "text": "Choose the word opposite in meaning to 'ARROGANT':",
                "explanation": "'Arrogant' means having an exaggerated sense of one's own importance; the direct opposite is 'humble'.",
                "options": [
                    ("A", "proud", False),
                    ("B", "haughty", False),
                    ("C", "humble", True),
                    ("D", "clever", False),
                    ("E", "timid", False),
                ],
            },
            {
                "num": 5,
                "text": "Select the sentence with the correct subject-verb agreement:",
                "explanation": "'Neither the teacher nor the students were' follows the proximity rule for compound subjects joined by 'neither...nor'.",
                "options": [
                    ("A", "Neither the teacher nor the students was present.", False),
                    ("B", "Neither the teacher nor the students were present.", True),
                    ("C", "Neither the teacher nor the students is present.", False),
                    ("D", "Neither the teacher nor the students has arrived.", False),
                    ("E", "Neither the teacher nor the students am present.", False),
                ],
            },
        ],
        2023: [  # SS2 Level
            {
                "num": 1,
                "text": "Choose the word that best completes the sentence:\nThe witness's testimony was completely ______ by documentary evidence.",
                "explanation": "'Corroborated' means confirmed or supported by other evidence.",
                "options": [
                    ("A", "corroborated", True),
                    ("B", "undermined", False),
                    ("C", "contradicted", False),
                    ("D", "dismissed", False),
                    ("E", "duplicated", False),
                ],
            },
            {
                "num": 2,
                "text": "Identify the grammatical function of the underlined clause in: 'What he said shocked everyone.'",
                "explanation": "'What he said' acts as a noun clause functioning as the subject of the verb 'shocked'.",
                "options": [
                    ("A", "Adverbial clause of reason", False),
                    ("B", "Adjectival clause qualifying everyone", False),
                    ("C", "Noun clause, subject of 'shocked'", True),
                    ("D", "Noun clause, object of 'shocked'", False),
                    ("E", "Parenthetical clause", False),
                ],
            },
            {
                "num": 3,
                "text": "Select the correct option with the appropriate vowel sound /i:/:",
                "explanation": "'Receipt' contains the long /i:/ sound in its second syllable.",
                "options": [
                    ("A", "Sit", False),
                    ("B", "Receipt", True),
                    ("C", "Threat", False),
                    ("D", "Bread", False),
                    ("E", "Dead", False),
                ],
            },
            {
                "num": 4,
                "text": "What is the meaning of the idiom 'to burn the midnight oil'?",
                "explanation": "'To burn the midnight oil' means to read, study, or work late into the night.",
                "options": [
                    ("A", "To waste kerosene or petrol", False),
                    ("B", "To study or work late into the night", True),
                    ("C", "To cause an accidental fire", False),
                    ("D", "To wake up very early at dawn", False),
                    ("E", "To cook dinner at midnight", False),
                ],
            },
            {
                "num": 5,
                "text": "Choose the word nearest in meaning to 'OBDURATE':",
                "explanation": "'Obdurate' means stubbornly refusing to change one's opinion or course of action; obstinate.",
                "options": [
                    ("A", "yielding", False),
                    ("B", "stubborn", True),
                    ("C", "gentle", False),
                    ("D", "fragile", False),
                    ("E", "flexible", False),
                ],
            },
        ],
        2024: [  # SS3 Level / JAMB-WAEC Prep
            {
                "num": 1,
                "text": "In the sentence 'Had I known about the changes, I would have prepared accordingly', the mood is:",
                "explanation": "The subjunctive mood expresses a hypothetical condition or a situation contrary to fact.",
                "options": [
                    ("A", "Indicative", False),
                    ("B", "Imperative", False),
                    ("C", "Subjunctive", True),
                    ("D", "Interrogative", False),
                    ("E", "Exclamatory", False),
                ],
            },
            {
                "num": 2,
                "text": "Choose the option with the correct primary stress for 'DEMOCRATIC':",
                "explanation": "Words ending in '-ic' typically take stress on the penultimate syllable: de-mo-CRAT-ic.",
                "options": [
                    ("A", "DE-mo-cra-tic", False),
                    ("B", "de-MO-cra-tic", False),
                    ("C", "de-mo-CRAT-ic", True),
                    ("D", "de-mo-cra-TIC", False),
                    ("E", "None of the above", False),
                ],
            },
            {
                "num": 3,
                "text": "Which of the following sentences illustrates a transferred epithet (hypallage)?",
                "explanation": "'He spent a sleepless night' transfers the human quality of sleeplessness onto the night.",
                "options": [
                    ("A", "The waves leapt high in the storm.", False),
                    ("B", "He spent a sleepless night tossing in bed.", True),
                    ("C", "Life is a stage for all mortals.", False),
                    ("D", "Silence is louder than words.", False),
                    ("E", "The kettle whistled happily.", False),
                ],
            },
            {
                "num": 4,
                "text": "Choose the word most opposite in meaning to 'EPHEMERAL':",
                "explanation": "'Ephemeral' means lasting for a very short time. Its antonym is 'eternal' or 'permanent'.",
                "options": [
                    ("A", "transient", False),
                    ("B", "fugitive", False),
                    ("C", "eternal", True),
                    ("D", "fleeting", False),
                    ("E", "momentary", False),
                ],
            },
            {
                "num": 5,
                "text": "Complete with the most appropriate idiom:\nAfter the long controversy, both parties finally agreed to ______ and work together.",
                "explanation": "'Bury the hatchet' means to settle differences, make peace, and end a conflict.",
                "options": [
                    ("A", "burn bridges", False),
                    ("B", "bury the hatchet", True),
                    ("C", "bite the dust", False),
                    ("D", "cut corners", False),
                    ("E", "break the ice", False),
                ],
            },
        ],
    },
    "Mathematics": {
        2022: [  # SS1 Level
            {
                "num": 1,
                "text": "Solve for x in the linear equation: 3(2x - 4) = 4(x + 1) + 2",
                "explanation": "6x - 12 = 4x + 4 + 2 => 6x - 12 = 4x + 6 => 2x = 18 => x = 9.",
                "options": [
                    ("A", "x = 5", False),
                    ("B", "x = 7", False),
                    ("C", "x = 9", True),
                    ("D", "x = 11", False),
                    ("E", "x = 13", False),
                ],
            },
            {
                "num": 2,
                "text": "Simplify the algebraic expression: (2x^3 * 3x^4) / (6x^2)",
                "explanation": "(6x^7) / (6x^2) = x^(7-2) = x^5.",
                "options": [
                    ("A", "x^3", False),
                    ("B", "x^4", False),
                    ("C", "x^5", True),
                    ("D", "6x^5", False),
                    ("E", "x^7", False),
                ],
            },
            {
                "num": 3,
                "text": "Find the sum of the interior angles of a regular hexagon (6 sides):",
                "explanation": "Formula: (n - 2) * 180° = (6 - 2) * 180° = 4 * 180° = 720°.",
                "options": [
                    ("A", "360°", False),
                    ("B", "540°", False),
                    ("C", "720°", True),
                    ("D", "900°", False),
                    ("E", "1080°", False),
                ],
            },
            {
                "num": 4,
                "text": "If log_10(2) = 0.3010 and log_10(3) = 0.4771, evaluate log_10(6):",
                "explanation": "log(6) = log(2 * 3) = log(2) + log(3) = 0.3010 + 0.4771 = 0.7781.",
                "options": [
                    ("A", "0.1436", False),
                    ("B", "0.7781", True),
                    ("C", "0.6020", False),
                    ("D", "0.9542", False),
                    ("E", "1.7781", False),
                ],
            },
            {
                "num": 5,
                "text": "Calculate the simple interest on ₦50,000 for 3 years at 5% per annum:",
                "explanation": "I = (P * R * T) / 100 = (50000 * 5 * 3) / 100 = ₦7,500.",
                "options": [
                    ("A", "₦2,500", False),
                    ("B", "₦5,000", False),
                    ("C", "₦7,500", True),
                    ("D", "₦10,000", False),
                    ("E", "₦15,000", False),
                ],
            },
        ],
        2023: [  # SS2 Level
            {
                "num": 1,
                "text": "Find the roots of the quadratic equation: 2x^2 - 5x - 3 = 0",
                "explanation": "Factoring: (2x + 1)(x - 3) = 0 => x = -1/2 or x = 3.",
                "options": [
                    ("A", "x = 1/2, x = -3", False),
                    ("B", "x = -1/2, x = 3", True),
                    ("C", "x = 2, x = -3", False),
                    ("D", "x = -1, x = 3/2", False),
                    ("E", "x = 1, x = 3", False),
                ],
            },
            {
                "num": 2,
                "text": "In a right-angled triangle, if opposite = 3 cm and adjacent = 4 cm, calculate the value of cos θ:",
                "explanation": "Hypotenuse = √(3^2 + 4^2) = 5 cm. cos θ = adjacent / hypotenuse = 4/5 = 0.8.",
                "options": [
                    ("A", "3/5", False),
                    ("B", "4/5", True),
                    ("C", "3/4", False),
                    ("D", "4/3", False),
                    ("E", "5/4", False),
                ],
            },
            {
                "num": 3,
                "text": "Find the 10th term of the Arithmetic Progression (AP): 3, 7, 11, 15, ...",
                "explanation": "a = 3, d = 4. T_10 = a + 9d = 3 + 9(4) = 3 + 36 = 39.",
                "options": [
                    ("A", "35", False),
                    ("B", "37", False),
                    ("C", "39", True),
                    ("D", "41", False),
                    ("E", "43", False),
                ],
            },
            {
                "num": 4,
                "text": "The angle of elevation of the top of a tower from a point 30 m away from its base on level ground is 45°. Find the height of the tower:",
                "explanation": "tan(45°) = height / 30 => 1 = height / 30 => height = 30 m.",
                "options": [
                    ("A", "15 m", False),
                    ("B", "20 m", False),
                    ("C", "30 m", True),
                    ("D", "45 m", False),
                    ("E", "60 m", False),
                ],
            },
            {
                "num": 5,
                "text": "A bag contains 5 red balls and 7 blue balls. A ball is drawn at random. What is the probability that it is red?",
                "explanation": "Total balls = 5 + 7 = 12. P(Red) = 5/12.",
                "options": [
                    ("A", "5/7", False),
                    ("B", "7/12", False),
                    ("C", "5/12", True),
                    ("D", "1/2", False),
                    ("E", "1/5", False),
                ],
            },
        ],
        2024: [  # SS3 Level / JAMB-WAEC Prep
            {
                "num": 1,
                "text": "Differentiate the function y = 3x^4 - 5x^2 + 2x - 7 with respect to x:",
                "explanation": "dy/dx = 4(3)x^3 - 2(5)x + 2 = 12x^3 - 10x + 2.",
                "options": [
                    ("A", "12x^3 - 10x + 2", True),
                    ("B", "12x^3 - 5x + 2", False),
                    ("C", "3x^3 - 10x + 2", False),
                    ("D", "12x^4 - 10x^2 + 2", False),
                    ("E", "7x^3 - 3x + 2", False),
                ],
            },
            {
                "num": 2,
                "text": "Evaluate the definite integral: ∫ from 0 to 2 of (3x^2 + 4x) dx:",
                "explanation": "[x^3 + 2x^2] from 0 to 2 = (2^3 + 2(2^2)) - 0 = 8 + 8 = 16.",
                "options": [
                    ("A", "12", False),
                    ("B", "14", False),
                    ("C", "16", True),
                    ("D", "18", False),
                    ("E", "20", False),
                ],
            },
            {
                "num": 3,
                "text": "Find the sum to infinity of the Geometric Progression: 16, 8, 4, 2, ...",
                "explanation": "a = 16, r = 1/2. S_∞ = a / (1 - r) = 16 / (1 - 0.5) = 16 / 0.5 = 32.",
                "options": [
                    ("A", "24", False),
                    ("B", "30", False),
                    ("C", "32", True),
                    ("D", "64", False),
                    ("E", "∞", False),
                ],
            },
            {
                "num": 4,
                "text": "Calculate the determinant of the 2x2 matrix: [[4, 2], [3, 5]]",
                "explanation": "Det = (4 * 5) - (2 * 3) = 20 - 6 = 14.",
                "options": [
                    ("A", "10", False),
                    ("B", "12", False),
                    ("C", "14", True),
                    ("D", "16", False),
                    ("E", "26", False),
                ],
            },
            {
                "num": 5,
                "text": "In how many distinct ways can 5 books be arranged on a single shelf?",
                "explanation": "Number of permutations = 5! = 5 * 4 * 3 * 2 * 1 = 120 ways.",
                "options": [
                    ("A", "25", False),
                    ("B", "60", False),
                    ("C", "120", True),
                    ("D", "240", False),
                    ("E", "720", False),
                ],
            },
        ],
    },
    "Physics": {
        2022: [  # SS1 Level
            {
                "num": 1,
                "text": "Which of the following is a fundamental physical quantity in the SI system?",
                "explanation": "Luminous intensity (candela), mass, length, time, electric current, temperature, and amount of substance are the 7 fundamental quantities.",
                "options": [
                    ("A", "Velocity", False),
                    ("B", "Force", False),
                    ("C", "Luminous Intensity", True),
                    ("D", "Acceleration", False),
                    ("E", "Pressure", False),
                ],
            },
            {
                "num": 2,
                "text": "A car accelerates uniformly from rest to a speed of 20 m/s in 5 seconds. Find its acceleration:",
                "explanation": "a = (v - u) / t = (20 - 0) / 5 = 4 m/s².",
                "options": [
                    ("A", "2 m/s²", False),
                    ("B", "4 m/s²", True),
                    ("C", "5 m/s²", False),
                    ("D", "10 m/s²", False),
                    ("E", "100 m/s²", False),
                ],
            },
            {
                "num": 3,
                "text": "Which law states that the extension in an elastic material is directly proportional to the applied force, provided the elastic limit is not exceeded?",
                "explanation": "Hooke's Law states F = ke within the proportional/elastic limit.",
                "options": [
                    ("A", "Ohm's Law", False),
                    ("B", "Hooke's Law", True),
                    ("C", "Newton's First Law", False),
                    ("D", "Pascal's Principle", False),
                    ("E", "Archimedes' Principle", False),
                ],
            },
            {
                "num": 4,
                "text": "An object of mass 10 kg is lifted to a height of 5 m above ground. What is its potential energy? (g = 9.8 m/s²)",
                "explanation": "PE = mgh = 10 * 9.8 * 5 = 490 J.",
                "options": [
                    ("A", "49 J", False),
                    ("B", "98 J", False),
                    ("C", "490 J", True),
                    ("D", "500 J", False),
                    ("E", "980 J", False),
                ],
            },
            {
                "num": 5,
                "text": "What type of thermometer is most suitable for measuring rapidly changing temperatures?",
                "explanation": "A thermoelectric thermometer (thermocouple) has a very small heat capacity and responds rapidly to temperature variations.",
                "options": [
                    ("A", "Clinical mercury thermometer", False),
                    ("B", "Alcohol-in-glass thermometer", False),
                    ("C", "Thermocouple thermometer", True),
                    ("D", "Constant volume gas thermometer", False),
                    ("E", "Bimetallic strip thermometer", False),
                ],
            },
        ],
        2023: [  # SS2 Level
            {
                "num": 1,
                "text": "A light ray travels from water (refractive index = 1.33) into air (refractive index = 1.0). What is the critical angle?",
                "explanation": "sin C = 1 / n = 1 / 1.33 = 0.7519 => C = arcsin(0.7519) ≈ 48.8°.",
                "options": [
                    ("A", "30.0°", False),
                    ("B", "41.8°", False),
                    ("C", "48.8°", True),
                    ("D", "60.0°", False),
                    ("E", "90.0°", False),
                ],
            },
            {
                "num": 2,
                "text": "The frequency of a sound wave is 500 Hz and its speed in air is 340 m/s. Calculate its wavelength:",
                "explanation": "v = f * λ => λ = v / f = 340 / 500 = 0.68 m.",
                "options": [
                    ("A", "0.34 m", False),
                    ("B", "0.68 m", True),
                    ("C", "1.47 m", False),
                    ("D", "170 m", False),
                    ("E", "840 m", False),
                ],
            },
            {
                "num": 3,
                "text": "Two resistors of 6 Ω and 3 Ω are connected in parallel. What is the equivalent resistance?",
                "explanation": "1/R = 1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2 => R = 2 Ω.",
                "options": [
                    ("A", "1.5 Ω", False),
                    ("B", "2.0 Ω", True),
                    ("C", "4.5 Ω", False),
                    ("D", "9.0 Ω", False),
                    ("E", "18.0 Ω", False),
                ],
            },
            {
                "num": 4,
                "text": "Which defect of vision is corrected by using a diverging (concave) lens?",
                "explanation": "Myopia (short-sightedness) is corrected using concave lenses to diverge light rays onto the retina.",
                "options": [
                    ("A", "Hypermetropia (long-sightedness)", False),
                    ("B", "Myopia (short-sightedness)", True),
                    ("C", "Astigmatism", False),
                    ("D", "Presbyopia", False),
                    ("E", "Glaucoma", False),
                ],
            },
            {
                "num": 5,
                "text": "Calculate the heat required to convert 2 kg of water at 100°C to steam at 100°C. (Specific latent heat of vaporization = 2.26 x 10^6 J/kg)",
                "explanation": "Q = m * L = 2 * 2.26 x 10^6 = 4.52 x 10^6 J = 4.52 MJ.",
                "options": [
                    ("A", "1.13 MJ", False),
                    ("B", "2.26 MJ", False),
                    ("C", "4.52 MJ", True),
                    ("D", "9.04 MJ", False),
                    ("E", "0.56 MJ", False),
                ],
            },
        ],
        2024: [  # SS3 Level
            {
                "num": 1,
                "text": "According to Einstein's photoelectric equation, the kinetic energy of emitted photoelectrons depends on:",
                "explanation": "KE_max = hf - W_0. It depends directly on the frequency (or energy) of the incident radiation.",
                "options": [
                    ("A", "Intensity of incident light", False),
                    ("B", "Frequency of incident light", True),
                    ("C", "Surface area of the metal", False),
                    ("D", "Temperature of the metal", False),
                    ("E", "Duration of exposure", False),
                ],
            },
            {
                "num": 2,
                "text": "A radioactive sample has a half-life of 4 days. If the initial mass is 80 g, what mass remains after 12 days?",
                "explanation": "Number of half-lives = 12 / 4 = 3. Remaining mass = 80 / (2^3) = 80 / 8 = 10 g.",
                "options": [
                    ("A", "40 g", False),
                    ("B", "20 g", False),
                    ("C", "10 g", True),
                    ("D", "5 g", False),
                    ("E", "2.5 g", False),
                ],
            },
            {
                "num": 3,
                "text": "Which particle is emitted when a Radium-226 nucleus undergoes alpha decay to Radon-222?",
                "explanation": "Alpha decay emits an alpha particle (Helium-4 nucleus: 2 protons, 2 neutrons).",
                "options": [
                    ("A", "An electron (beta particle)", False),
                    ("B", "A positron", False),
                    ("C", "A Helium-4 nucleus (alpha particle)", True),
                    ("D", "A high-energy photon (gamma ray)", False),
                    ("E", "A neutron", False),
                ],
            },
            {
                "num": 4,
                "text": "Calculate the de Broglie wavelength of an electron (mass = 9.1 x 10^-31 kg) moving at 1.0 x 10^6 m/s. (h = 6.63 x 10^-34 J·s)",
                "explanation": "λ = h / (m * v) = 6.63e-34 / (9.1e-31 * 1.0e6) = 6.63e-34 / 9.1e-25 ≈ 7.28 x 10^-10 m = 0.728 nm.",
                "options": [
                    ("A", "0.728 nm", True),
                    ("B", "1.456 nm", False),
                    ("C", "3.640 nm", False),
                    ("D", "7.280 nm", False),
                    ("E", "0.072 nm", False),
                ],
            },
            {
                "num": 5,
                "text": "In an AC circuit containing only a pure inductor of inductance L, the current:",
                "explanation": "In a pure inductor (ELI), the voltage leads the current by 90°, which means current lags voltage by 90° (π/2 radians).",
                "options": [
                    ("A", "Leads the voltage by 90°", False),
                    ("B", "Lags the voltage by 90°", True),
                    ("C", "Is in phase with the voltage", False),
                    ("D", "Lags the voltage by 180°", False),
                    ("E", "Leads the voltage by 45°", False),
                ],
            },
        ],
    },
    "Chemistry": {
        2022: [  # SS1 Level
            {
                "num": 1,
                "text": "Which of the following is a chemical change?",
                "explanation": "Rusting of iron involves chemical reaction with oxygen and water forming iron oxide (new chemical bonds).",
                "options": [
                    ("A", "Melting of candle wax", False),
                    ("B", "Dissolving salt in water", False),
                    ("C", "Rusting of an iron nail", True),
                    ("D", "Evaporation of ethanol", False),
                    ("E", "Sublimation of iodine", False),
                ],
            },
            {
                "num": 2,
                "text": "An atom has an atomic number of 17 and mass number of 35. How many neutrons does it contain?",
                "explanation": "Number of neutrons = Mass number - Atomic number = 35 - 17 = 18 neutrons.",
                "options": [
                    ("A", "17", False),
                    ("B", "18", True),
                    ("C", "35", False),
                    ("D", "52", False),
                    ("E", "19", False),
                ],
            },
            {
                "num": 3,
                "text": "What type of chemical bonding involves the sharing of pairs of electrons between non-metal atoms?",
                "explanation": "Covalent bonding is formed by the electrostatic attraction between positive nuclei and shared electron pairs.",
                "options": [
                    ("A", "Ionic bonding", False),
                    ("B", "Covalent bonding", True),
                    ("C", "Metallic bonding", False),
                    ("D", "Hydrogen bonding", False),
                    ("E", "Van der Waals forces", False),
                ],
            },
            {
                "num": 4,
                "text": "Which of the following gas laws states that equal volumes of all gases at the same temperature and pressure contain equal numbers of molecules?",
                "explanation": "Avogadro's Law states V ∝ n at constant temperature and pressure.",
                "options": [
                    ("A", "Boyle's Law", False),
                    ("B", "Charles's Law", False),
                    ("C", "Avogadro's Law", True),
                    ("D", "Graham's Law", False),
                    ("E", "Dalton's Law", False),
                ],
            },
            {
                "num": 5,
                "text": "What is the pH value of a neutral aqueous solution at 25°C?",
                "explanation": "At 25°C, [H+] = [OH-] = 10^-7 M, resulting in a neutral pH of 7.",
                "options": [
                    ("A", "0", False),
                    ("B", "3", False),
                    ("C", "7", True),
                    ("D", "10", False),
                    ("E", "14", False),
                ],
            },
        ],
        2023: [  # SS2 Level
            {
                "num": 1,
                "text": "Which product is liberated at the cathode during the electrolysis of acidified water using platinum electrodes?",
                "explanation": "Hydrogen ions (2H+ + 2e- -> H2) are reduced at the cathode, releasing Hydrogen gas.",
                "options": [
                    ("A", "Oxygen gas", False),
                    ("B", "Hydrogen gas", True),
                    ("C", "Sulfur dioxide", False),
                    ("D", "Chlorine gas", False),
                    ("E", "Water vapor", False),
                ],
            },
            {
                "num": 2,
                "text": "Determine the oxidation state of Chromium in Potassium dichromate (K2Cr2O7):",
                "explanation": "2(+1) + 2(Cr) + 7(-2) = 0 => 2 + 2(Cr) - 14 = 0 => 2(Cr) = 12 => Cr = +6.",
                "options": [
                    ("A", "+3", False),
                    ("B", "+4", False),
                    ("C", "+6", True),
                    ("D", "+7", False),
                    ("E", "-2", False),
                ],
            },
            {
                "num": 3,
                "text": "What is the IUPAC name for the organic compound CH3-CH2-CHO?",
                "explanation": "A 3-carbon chain containing an aldehyde functional group (-CHO) is propanal.",
                "options": [
                    ("A", "Propan-1-ol", False),
                    ("B", "Propanone", False),
                    ("C", "Propanal", True),
                    ("D", "Propanoic acid", False),
                    ("E", "Ethyl methanoate", False),
                ],
            },
            {
                "num": 4,
                "text": "According to Le Chatelier's principle, increasing the pressure on the system: N2(g) + 3H2(g) ⇌ 2NH3(g) will:",
                "explanation": "Increasing pressure shifts equilibrium toward the side with fewer gas moles (4 moles -> 2 moles NH3).",
                "options": [
                    ("A", "Shift equilibrium to the left", False),
                    ("B", "Increase the yield of Ammonia (NH3)", True),
                    ("C", "Have no effect on equilibrium", False),
                    ("D", "Decrease the rate of reaction", False),
                    ("E", "Decompose ammonia into nitrogen", False),
                ],
            },
            {
                "num": 5,
                "text": "The laboratory test for unsaturation in alkenes utilizes:",
                "explanation": "Bromine water or acidified KMnO4 decolourizes when reacted with carbon-carbon double bonds in alkenes.",
                "options": [
                    ("A", "Fehling's solution", False),
                    ("B", "Tollens' reagent", False),
                    ("C", "Decolourization of Bromine water", True),
                    ("D", "Litmus paper turning blue", False),
                    ("E", "Sodium metal test", False),
                ],
            },
        ],
        2024: [  # SS3 Level
            {
                "num": 1,
                "text": "Calculate the standard enthalpy change of reaction (ΔH°) for: CH4 + 2O2 -> CO2 + 2H2O given:\nΔHf(CH4) = -75 kJ/mol, ΔHf(CO2) = -394 kJ/mol, ΔHf(H2O) = -286 kJ/mol.",
                "explanation": "ΔH = [(-394) + 2(-286)] - [-75] = [-394 - 572] + 75 = -966 + 75 = -891 kJ/mol.",
                "options": [
                    ("A", "-891 kJ/mol", True),
                    ("B", "-605 kJ/mol", False),
                    ("C", "+891 kJ/mol", False),
                    ("D", "-966 kJ/mol", False),
                    ("E", "-75 kJ/mol", False),
                ],
            },
            {
                "num": 2,
                "text": "What type of isomerism is exhibited by But-1-ene and But-2-ene?",
                "explanation": "Position isomerism arises because the functional double bond is in different positions on the same carbon skeleton.",
                "options": [
                    ("A", "Chain isomerism", False),
                    ("B", "Positional isomerism", True),
                    ("C", "Functional group isomerism", False),
                    ("D", "Geometric (cis-trans) isomerism", False),
                    ("E", "Optical isomerism", False),
                ],
            },
            {
                "num": 3,
                "text": "In the Haber Process for manufacturing Ammonia, what is the optimal catalyst employed?",
                "explanation": "Finely divided iron (Fe) promoted with potassium and aluminium oxides is the industrial catalyst.",
                "options": [
                    ("A", "Vanadium(V) oxide (V2O5)", False),
                    ("B", "Finely divided Iron (Fe)", True),
                    ("C", "Platinum gauze", False),
                    ("D", "Nickel powder", False),
                    ("E", "Concentrated H2SO4", False),
                ],
            },
            {
                "num": 4,
                "text": "Which of the following organic reactions converts vegetable oil into margarine (solid fat)?",
                "explanation": "Catalytic hydrogenation adds hydrogen across double bonds in unsaturated oils using a nickel catalyst.",
                "options": [
                    ("A", "Saponification", False),
                    ("B", "Catalytic Hydrogenation", True),
                    ("C", "Esterification", False),
                    ("D", "Polymerization", False),
                    ("E", "Decarboxylation", False),
                ],
            },
            {
                "num": 5,
                "text": "The spontaneous feasibility of a chemical process requires the Gibbs Free Energy change (ΔG) to be:",
                "explanation": "A reaction is thermodynamically spontaneous when ΔG = ΔH - TΔS < 0 (negative).",
                "options": [
                    ("A", "Positive (> 0)", False),
                    ("B", "Negative (< 0)", True),
                    ("C", "Zero (= 0)", False),
                    ("D", "Equal to activation energy", False),
                    ("E", "Infinite", False),
                ],
            },
        ],
    },
    "Biology": {
        2022: [  # SS1 Level
            {
                "num": 1,
                "text": "Which organelle is referred to as the 'powerhouse of the cell' due to ATP generation?",
                "explanation": "Mitochondria produce cellular ATP through oxidative aerobic respiration.",
                "options": [
                    ("A", "Ribosome", False),
                    ("B", "Golgi apparatus", False),
                    ("C", "Mitochondrion", True),
                    ("D", "Nucleus", False),
                    ("E", "Endoplasmic reticulum", False),
                ],
            },
            {
                "num": 2,
                "text": "The movement of water molecules from a region of lower solute concentration to higher solute concentration across a semi-permeable membrane is:",
                "explanation": "Osmosis is the passive diffusion of solvent (water) across a selectively permeable membrane.",
                "options": [
                    ("A", "Active transport", False),
                    ("B", "Diffusion", False),
                    ("C", "Osmosis", True),
                    ("D", "Plasmolysis", False),
                    ("E", "Transpiration", False),
                ],
            },
            {
                "num": 3,
                "text": "Which blood group is referred to as the 'universal donor'?",
                "explanation": "Blood group O negative has neither A nor B surface antigens on erythrocytes.",
                "options": [
                    ("A", "Group A", False),
                    ("B", "Group B", False),
                    ("C", "Group AB", False),
                    ("D", "Group O", True),
                    ("E", "Group Rh+", False),
                ],
            },
            {
                "num": 4,
                "text": "The process by which green plants manufacture carbohydrates using carbon dioxide, water, and sunlight is:",
                "explanation": "Photosynthesis converts solar energy into chemical energy in chloroplasts.",
                "options": [
                    ("A", "Respiration", False),
                    ("B", "Photosynthesis", True),
                    ("C", "Chemosynthesis", False),
                    ("D", "Fermentation", False),
                    ("E", "Translocation", False),
                ],
            },
            {
                "num": 5,
                "text": "In the human digestive system, bile is produced in the ______ and stored in the ______.",
                "explanation": "Bile is synthesized by hepatocytes in the liver and concentrated in the gall bladder.",
                "options": [
                    ("A", "Stomach, Pancreas", False),
                    ("B", "Liver, Gall bladder", True),
                    ("C", "Pancreas, Small intestine", False),
                    ("D", "Gall bladder, Liver", False),
                    ("E", "Duodenum, Spleen", False),
                ],
            },
        ],
        2023: [  # SS2 Level
            {
                "num": 1,
                "text": "Which plant hormone is primarily responsible for apical dominance and cell elongation?",
                "explanation": "Auxin (indole-3-acetic acid) promotes stem elongation and suppresses lateral bud outgrowth.",
                "options": [
                    ("A", "Gibberellin", False),
                    ("B", "Auxin", True),
                    ("C", "Cytokinin", False),
                    ("D", "Abscisic acid", False),
                    ("E", "Ethylene", False),
                ],
            },
            {
                "num": 2,
                "text": "The structural and functional unit of the mammalian kidney is the:",
                "explanation": "The nephron carries out ultrafiltration, selective reabsorption, and urine production.",
                "options": [
                    ("A", "Neuron", False),
                    ("B", "Nephron", True),
                    ("C", "Alveolus", False),
                    ("D", "Villus", False),
                    ("E", "Hepatocyte", False),
                ],
            },
            {
                "num": 3,
                "text": "In a cross between two heterozygous tall pea plants (Tt x Tt), what proportion of the offspring will be dwarf (tt)?",
                "explanation": "Mendelian monohybrid cross yields 1 TT : 2 Tt : 1 tt, so 1/4 (25%) are homozygous recessive dwarf.",
                "options": [
                    ("A", "100%", False),
                    ("B", "75%", False),
                    ("C", "50%", False),
                    ("D", "25%", True),
                    ("E", "0%", False),
                ],
            },
            {
                "num": 4,
                "text": "What type of ecological relationship exists between nitrogen-fixing bacteria (Rhizobium) and leguminous plant roots?",
                "explanation": "Mutualism is an association in which both organisms derive mutual benefits.",
                "options": [
                    ("A", "Parasitism", False),
                    ("B", "Mutualism", True),
                    ("C", "Commensalism", False),
                    ("D", "Predation", False),
                    ("E", "Amensalism", False),
                ],
            },
            {
                "num": 5,
                "text": "The part of the human brain responsible for maintaining posture, balance, and muscle coordination is:",
                "explanation": "The cerebellum coordinates voluntary motor movements and body equilibrium.",
                "options": [
                    ("A", "Cerebrum", False),
                    ("B", "Cerebellum", True),
                    ("C", "Medulla oblongata", False),
                    ("D", "Hypothalamus", False),
                    ("E", "Thalamus", False),
                ],
            },
        ],
        2024: [  # SS3 Level
            {
                "num": 1,
                "text": "Which nucleotide base pairs specifically with Cytosine in DNA via three hydrogen bonds?",
                "explanation": "In DNA base pairing rules (Chargaff), Guanine pairs exclusively with Cytosine (G≡C).",
                "options": [
                    ("A", "Adenine", False),
                    ("B", "Thymine", False),
                    ("C", "Guanine", True),
                    ("D", "Uracil", False),
                    ("E", "Ribose", False),
                ],
            },
            {
                "num": 2,
                "text": "The Darwinian evolutionary mechanism of 'survival of the fittest' operates through:",
                "explanation": "Natural selection favors organisms with phenotypic traits best suited to their environment.",
                "options": [
                    ("A", "Use and disuse of organs", False),
                    ("B", "Natural Selection", True),
                    ("C", "Artificial breeding only", False),
                    ("D", "Spontaneous generation", False),
                    ("E", "Acquired characteristics inheritance", False),
                ],
            },
            {
                "num": 3,
                "text": "Sickle-cell anaemia in humans is caused by a point mutation in the beta-globin gene, resulting in the substitution of:",
                "explanation": "Glutamic acid is replaced by Valine at position 6 of the beta-globin polypeptide chain.",
                "options": [
                    ("A", "Valine by Glutamic acid", False),
                    ("B", "Glutamic acid by Valine", True),
                    ("C", "Lysine by Alanine", False),
                    ("D", "Glycine by Proline", False),
                    ("E", "Serine by Leucine", False),
                ],
            },
            {
                "num": 4,
                "text": "Which endocrine hormone stimulates the uterine contractions during childbirth in mammals?",
                "explanation": "Oxytocin, released by the posterior pituitary, stimulates forceful uterine myometrial contractions.",
                "options": [
                    ("A", "Prolactin", False),
                    ("B", "Progesterone", False),
                    ("C", "Oxytocin", True),
                    ("D", "Estrogen", False),
                    ("E", "Luteinizing hormone", False),
                ],
            },
            {
                "num": 5,
                "text": "The stage of meiosis during which homologous chromosomes pair up and crossing over occurs is:",
                "explanation": "Prophase I (specifically the pachytene substage) is when synapsis and genetic recombination take place.",
                "options": [
                    ("A", "Prophase I", True),
                    ("B", "Metaphase I", False),
                    ("C", "Anaphase II", False),
                    ("D", "Telophase I", False),
                    ("E", "Interphase", False),
                ],
            },
        ],
    },
    "Economics": {
        2022: [
            {
                "num": 1,
                "text": "The fundamental economic problem in all human societies is:",
                "explanation": "Scarcity of productive resources in the presence of unlimited human wants creates the basic economic problem.",
                "options": [
                    ("A", "High taxation", False),
                    ("B", "Scarcity of resources relative to unlimited wants", True),
                    ("C", "Lack of money", False),
                    ("D", "Unemployment only", False),
                    ("E", "Poor banking facilities", False),
                ],
            },
            {
                "num": 2,
                "text": "The value of the next best alternative forgone when a choice is made is known as:",
                "explanation": "Opportunity cost represents the true cost of making a choice in terms of the sacrificed alternative.",
                "options": [
                    ("A", "Real cost", False),
                    ("B", "Opportunity cost", True),
                    ("C", "Money cost", False),
                    ("D", "Variable cost", False),
                    ("E", "Marginal cost", False),
                ],
            },
            {
                "num": 3,
                "text": "According to the Law of Demand, as the price of a normal good increases, ceteris paribus:",
                "explanation": "Price and quantity demanded have an inverse relationship for normal goods.",
                "options": [
                    ("A", "Quantity demanded increases", False),
                    ("B", "Quantity demanded decreases", True),
                    ("C", "Quantity supplied decreases", False),
                    ("D", "Demand curve shifts to the right", False),
                    ("E", "Equilibrium price falls", False),
                ],
            },
            {
                "num": 4,
                "text": "Which factor of production receives 'Interest' as its economic reward?",
                "explanation": "Capital receives interest, land receives rent, labor receives wages, and entrepreneurship receives profit.",
                "options": [
                    ("A", "Land", False),
                    ("B", "Labor", False),
                    ("C", "Capital", True),
                    ("D", "Entrepreneur", False),
                    ("E", "Management", False),
                ],
            },
            {
                "num": 5,
                "text": "A market structure characterized by a single seller of a unique product with no close substitutes is a:",
                "explanation": "Monopoly is defined by a single supplier having complete market control.",
                "options": [
                    ("A", "Perfect competition", False),
                    ("B", "Monopoly", True),
                    ("C", "Oligopoly", False),
                    ("D", "Monopolistic competition", False),
                    ("E", "Duopoly", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "If a 10% rise in price leads to a 20% fall in quantity demanded, price elasticity of demand is:",
                "explanation": "Elasticity = %ΔQ / %ΔP = 20% / 10% = 2.0 (Elastic demand).",
                "options": [
                    ("A", "0.5 (Inelastic)", False),
                    ("B", "1.0 (Unitary)", False),
                    ("C", "2.0 (Elastic)", True),
                    ("D", "0.2 (Inelastic)", False),
                    ("E", "Infinite (Perfect)", False),
                ],
            },
            {
                "num": 2,
                "text": "Gross Domestic Product (GDP) measures:",
                "explanation": "GDP is the monetary market value of all final goods and services produced within the domestic borders in a given year.",
                "options": [
                    ("A", "Total money in circulation", False),
                    ("B", "Total market value of all final goods and services produced domestically in a year", True),
                    ("C", "Total exports minus imports only", False),
                    ("D", "Total tax revenue collected by the government", False),
                    ("E", "Total wealth of citizens abroad", False),
                ],
            },
            {
                "num": 3,
                "text": "Which monetary policy tool is used by the Central Bank to reduce money supply and control inflation?",
                "explanation": "Increasing the Cash Reserve Ratio (CRR) or Monetary Policy Rate (MPR) restricts commercial bank lending.",
                "options": [
                    ("A", "Lowering the Monetary Policy Rate (MPR)", False),
                    ("B", "Raising the Cash Reserve Ratio (CRR)", True),
                    ("C", "Buying government treasury bills on Open Market", False),
                    ("D", "Reducing personal income tax", False),
                    ("E", "Increasing government expenditure", False),
                ],
            },
            {
                "num": 4,
                "text": "Cost-push inflation is typically caused by:",
                "explanation": "Cost-push inflation occurs when production costs (wages, raw materials, energy) rise, shifting aggregate supply left.",
                "options": [
                    ("A", "Excessive consumer aggregate demand", False),
                    ("B", "Substantial increases in the cost of production inputs", True),
                    ("C", "Reduction in government debt", False),
                    ("D", "Surplus agricultural harvest", False),
                    ("E", "Appreciation of domestic currency", False),
                ],
            },
            {
                "num": 5,
                "text": "The law of diminishing marginal returns states that as successive units of a variable input are added to fixed inputs:",
                "explanation": "Marginal product will eventually decline after an optimal input ratio is reached.",
                "options": [
                    ("A", "Total product immediately drops to zero", False),
                    ("B", "The extra output per additional unit of variable input eventually decreases", True),
                    ("C", "Costs of production become negative", False),
                    ("D", "Fixed costs increase exponentially", False),
                    ("E", "Profits become infinite", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "The principle of comparative advantage in international trade states that a country should specialize in exporting goods that it produces with:",
                "explanation": "Comparative advantage is based on having a lower opportunity cost relative to trading partners.",
                "options": [
                    ("A", "Higher absolute costs", False),
                    ("B", "Lower opportunity cost", True),
                    ("C", "The largest labor force", False),
                    ("D", "The highest tariffs", False),
                    ("E", "Zero capital requirement", False),
                ],
            },
            {
                "num": 2,
                "text": "In national income accounting, Net National Product (NNP) is obtained by:",
                "explanation": "NNP = Gross National Product (GNP) minus Capital Depreciation (Capital Consumption Allowance).",
                "options": [
                    ("A", "GNP + Depreciation", False),
                    ("B", "GNP - Depreciation (Capital Consumption)", True),
                    ("C", "GDP - Subsidies", False),
                    ("D", "Personal Income - Taxes", False),
                    ("E", "Exports - Imports", False),
                ],
            },
            {
                "num": 3,
                "text": "A progressive tax system is one in which:",
                "explanation": "In progressive taxation, the tax rate increases as the taxpayer's income increases.",
                "options": [
                    ("A", "Everyone pays the exact same flat amount", False),
                    ("B", "Higher income earners pay a higher proportion/percentage of their income", True),
                    ("C", "Lower income earners pay higher rates than wealthy citizens", False),
                    ("D", "Only corporations pay taxes", False),
                    ("E", "Tax rates drop as earnings grow", False),
                ],
            },
            {
                "num": 4,
                "text": "If the marginal propensity to consume (MPC) is 0.8, calculate the simple Keynesian investment multiplier:",
                "explanation": "Multiplier k = 1 / (1 - MPC) = 1 / (1 - 0.8) = 1 / 0.2 = 5.",
                "options": [
                    ("A", "2", False),
                    ("B", "4", False),
                    ("C", "5", True),
                    ("D", "8", False),
                    ("E", "10", False),
                ],
            },
            {
                "num": 5,
                "text": "Devaluation of a nation's currency will improve its balance of payments trade deficit provided:",
                "explanation": "The Marshall-Lerner condition states devaluation improves trade balance if (Elasticity of Exports + Elasticity of Imports) > 1.",
                "options": [
                    ("A", "The Marshall-Lerner condition is satisfied (Sum of price elasticities of exports and imports > 1)", True),
                    ("B", "Tariffs are completely abolished", False),
                    ("C", "Domestic inflation exceeds global inflation", False),
                    ("D", "Foreign exchange reserves are exhausted", False),
                    ("E", "Interest rates are set to zero", False),
                ],
            },
        ],
    },
    "Government": {
        2022: [
            {
                "num": 1,
                "text": "Which of the following is an essential characteristic of a sovereign state?",
                "explanation": "A state must have defined territory, permanent population, government, and sovereign independence.",
                "options": [
                    ("A", "Military regime", False),
                    ("B", "Defined territory and sovereignty", True),
                    ("C", "Monarchy system", False),
                    ("D", "Unitary constitution", False),
                    ("E", "One-party democracy", False),
                ],
            },
            {
                "num": 2,
                "text": "The doctrine of 'Separation of Powers' was popularized by which political philosopher?",
                "explanation": "Baron de Montesquieu articulated the trias politica model in 'The Spirit of the Laws' (1748).",
                "options": [
                    ("A", "John Locke", False),
                    ("B", "Thomas Hobbes", False),
                    ("C", "Baron de Montesquieu", True),
                    ("D", "Karl Marx", False),
                    ("E", "Jean-Jacques Rousseau", False),
                ],
            },
            {
                "num": 3,
                "text": "Rule of Law implies:",
                "explanation": "The Rule of Law ensures supremacy of regular law, equality before the law, and protection of human rights.",
                "options": [
                    ("A", "The military rules without challenge", False),
                    ("B", "Equality of all citizens before the law and supremacy of the constitution", True),
                    ("C", "The executive is above the judiciary", False),
                    ("D", "Only lawyers can hold public office", False),
                    ("E", "Arbitrary detention by state police", False),
                ],
            },
            {
                "num": 4,
                "text": "A system of government where power is shared between a central authority and constituent regional units is a:",
                "explanation": "Federalism divides constitutional powers between national and regional/state governments.",
                "options": [
                    ("A", "Unitary system", False),
                    ("B", "Confederal system", False),
                    ("C", "Federal system", True),
                    ("D", "Monarchical system", False),
                    ("E", "Feudal system", False),
                ],
            },
            {
                "num": 5,
                "text": "Which arm of government is constitutionally empowered to interpret laws?",
                "explanation": "The Judiciary interprets laws, the Legislature enacts laws, and the Executive enforces laws.",
                "options": [
                    ("A", "The Executive", False),
                    ("B", "The Legislature", False),
                    ("C", "The Judiciary", True),
                    ("D", "The Civil Service", False),
                    ("E", "The Armed Forces", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "The 1922 Clifford Constitution in Nigeria was historically significant because it introduced the:",
                "explanation": "The Clifford Constitution of 1922 introduced the Elective Principle for seats in Lagos and Calabar.",
                "options": [
                    ("A", "Federal system of government", False),
                    ("B", "Elective Principle in Nigerian politics", True),
                    ("C", "Bicameral national parliament", False),
                    ("D", "Office of the Prime Minister", False),
                    ("E", "Supreme Court of Nigeria", False),
                ],
            },
            {
                "num": 2,
                "text": "Under the British colonial administration, 'Indirect Rule' relied primarily on:",
                "explanation": "Indirect Rule governed the local populace through traditional rulers and existing indigenous institutions.",
                "options": [
                    ("A", "Direct military garrison governors", False),
                    ("B", "Traditional rulers and native authorities", True),
                    ("C", "Elected democratic parliaments", False),
                    ("D", "French assimilation policies", False),
                    ("E", "Trade union leaders", False),
                ],
            },
            {
                "num": 3,
                "text": "Which Nigerian constitution officially created a three-region federal structure (North, East, West)?",
                "explanation": "The 1954 Lyttelton Constitution established a genuine federal framework with regional autonomy.",
                "options": [
                    ("A", "Clifford Constitution (1922)", False),
                    ("B", "Richards Constitution (1946)", False),
                    ("C", "Macpherson Constitution (1951)", False),
                    ("D", "Lyttelton Constitution (1954)", True),
                    ("E", "1979 Constitution", False),
                ],
            },
            {
                "num": 4,
                "text": "The primary role of the Public Complaints Commission (Ombudsman) is to:",
                "explanation": "An Ombudsman investigates citizen complaints against administrative injustice and bureaucratic abuse.",
                "options": [
                    ("A", "Conduct general elections", False),
                    ("B", "Investigate citizens' complaints against administrative injustice and corruption", True),
                    ("C", "Draft national bills", False),
                    ("D", "Collect federal taxes", False),
                    ("E", "Command military forces", False),
                ],
            },
            {
                "num": 5,
                "text": "Franchise in modern democratic government refers to the:",
                "explanation": "Franchise (or suffrage) is the constitutional right to vote and stand for public elections.",
                "options": [
                    ("A", "Right to own private business", False),
                    ("B", "Constitutional right to vote and be voted for", True),
                    ("C", "Power of judicial review", False),
                    ("D", "Immunity granted to foreign diplomats", False),
                    ("E", "Freedom of international travel", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "In a Parliamentary system of government (such as Britain), the Head of Government is the:",
                "explanation": "In parliamentary democracies, the Prime Minister heads government while the Monarch or President is ceremonial Head of State.",
                "options": [
                    ("A", "President", False),
                    ("B", "Prime Minister", True),
                    ("C", "Chief Justice", False),
                    ("D", "Speaker of the House", False),
                    ("E", "Cabinet Secretary", False),
                ],
            },
            {
                "num": 2,
                "text": "Which international organization was founded in 1975 to foster economic integration across West Africa?",
                "explanation": "ECOWAS (Economic Community of West African States) was established by the Treaty of Lagos on May 28, 1975.",
                "options": [
                    ("A", "African Union (AU)", False),
                    ("B", "ECOWAS", True),
                    ("C", "OPEC", False),
                    ("D", "Commonwealth of Nations", False),
                    ("E", "United Nations", False),
                ],
            },
            {
                "num": 3,
                "text": "Which organ of the United Nations has primary responsibility for maintaining international peace and security?",
                "explanation": "The UN Security Council (UNSC) has 5 permanent veto members and 10 non-permanent members dedicated to peace and security.",
                "options": [
                    ("A", "General Assembly", False),
                    ("B", "International Court of Justice", False),
                    ("C", "Security Council", True),
                    ("D", "Economic and Social Council", False),
                    ("E", "Trusteeship Council", False),
                ],
            },
            {
                "num": 4,
                "text": "A vote of 'No Confidence' in a parliamentary democracy leads to:",
                "explanation": "When the legislature passes a vote of no confidence, the Prime Minister and cabinet must resign or dissolve parliament.",
                "options": [
                    ("A", "Immediate military takeover", False),
                    ("B", "Resignation of the Prime Minister and cabinet", True),
                    ("C", "Suspension of the constitution", False),
                    ("D", "Dismissal of all judges", False),
                    ("E", "State of emergency declaration", False),
                ],
            },
            {
                "num": 5,
                "text": "A key feature of the Non-Aligned Movement (NAM) during the Cold War was:",
                "explanation": "NAM nations chose not to formally align with either the Western (US/NATO) or Eastern (Soviet/Warsaw) power blocs.",
                "options": [
                    ("A", "Military alliance with the Soviet Union", False),
                    ("B", "Neutrality and non-membership in major superpower military blocs", True),
                    ("C", "Adoption of a single worldwide currency", False),
                    ("D", "Subordination to the Warsaw Pact", False),
                    ("E", "Total boycott of global commerce", False),
                ],
            },
        ],
    },
    "Literature in English": {
        2022: [
            {
                "num": 1,
                "text": "A poem of fourteen lines with a structured rhyme scheme is known as a:",
                "explanation": "A sonnet is a 14-line poetic form (Petrarchan or Shakespearean).",
                "options": [
                    ("A", "Ballad", False),
                    ("B", "Elegy", False),
                    ("C", "Sonnet", True),
                    ("D", "Ode", False),
                    ("E", "Epic", False),
                ],
            },
            {
                "num": 2,
                "text": "The main character or hero of a literary work who faces the central conflict is the:",
                "explanation": "The protagonist is the principal character in a drama or narrative.",
                "options": [
                    ("A", "Antagonist", False),
                    ("B", "Protagonist", True),
                    ("C", "Foil", False),
                    ("D", "Chorus", False),
                    ("E", "Narrator", False),
                ],
            },
            {
                "num": 3,
                "text": "An explicit comparison between two dissimilar things using 'like' or 'as' is a:",
                "explanation": "Simile uses connective words 'like' or 'as' to compare things.",
                "options": [
                    ("A", "Metaphor", False),
                    ("B", "Simile", True),
                    ("C", "Irony", False),
                    ("D", "Hyperbole", False),
                    ("E", "Oxymoron", False),
                ],
            },
            {
                "num": 4,
                "text": "A mournful poem written to lament the death of a person is an:",
                "explanation": "An elegy is a formal lyric poem lamenting the death of an individual or mortality.",
                "options": [
                    ("A", "Ode", False),
                    ("B", "Sonnet", False),
                    ("C", "Elegy", True),
                    ("D", "Epic", False),
                    ("E", "Limerick", False),
                ],
            },
            {
                "num": 5,
                "text": "In drama, when an actor speaks their thoughts aloud while alone on stage, it is a:",
                "explanation": "A soliloquy is a dramatic monologue revealing a character's inner thoughts to the audience.",
                "options": [
                    ("A", "Dialogue", False),
                    ("B", "Prologue", False),
                    ("C", "Soliloquy", True),
                    ("D", "Aside", False),
                    ("E", "Epilogue", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "The repetition of consonant sounds at the beginning of adjacent words (e.g. 'sweet birds sang sweetly') is:",
                "explanation": "Alliteration is the repetition of initial consonant sounds in neighboring words.",
                "options": [
                    ("A", "Assonance", False),
                    ("B", "Alliteration", True),
                    ("C", "Onomatopoeia", False),
                    ("D", "Consonance", False),
                    ("E", "Rhyme", False),
                ],
            },
            {
                "num": 2,
                "text": "The emotional purging and cleansing experienced by the audience at the climax of a tragedy is:",
                "explanation": "Catharsis is Aristotle's term for the emotional release of pity and fear evoked by tragedy.",
                "options": [
                    ("A", "Hamartia", False),
                    ("B", "Catharsis", True),
                    ("C", "Hubris", False),
                    ("D", "Nemesis", False),
                    ("E", "Anagnorisis", False),
                ],
            },
            {
                "num": 3,
                "text": "In Chinua Achebe's classic novel 'Things Fall Apart', the protagonist is:",
                "explanation": "Okonkwo is the famed warrior and protagonist of Achebe's 'Things Fall Apart'.",
                "options": [
                    ("A", "Obierika", False),
                    ("B", "Okonkwo", True),
                    ("C", "Unoka", False),
                    ("D", "Nwoye", False),
                    ("E", "Ikemefuna", False),
                ],
            },
            {
                "num": 4,
                "text": "When a character's tragic flaw or error in judgment brings about their downfall, it is termed:",
                "explanation": "Hamartia refers to the tragic flaw or fatal error leading to the protagonist's catastrophe.",
                "options": [
                    ("A", "Hubris", False),
                    ("B", "Hamartia", True),
                    ("C", "Catharsis", False),
                    ("D", "Peripeteia", False),
                    ("E", "Denouement", False),
                ],
            },
            {
                "num": 5,
                "text": "The resolution or unknotting of the plot complications following the climax in a story is the:",
                "explanation": "Denouement is the final unfolding and resolution of the dramatic plot.",
                "options": [
                    ("A", "Exposition", False),
                    ("B", "Climax", False),
                    ("C", "Denouement", True),
                    ("D", "Rising action", False),
                    ("E", "Foreshadowing", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "In Wole Soyinka's play 'The Lion and the Jewel', the village beauty courted by both Lakunle and Baroka is:",
                "explanation": "Sidi is the village belle sought by modern teacher Lakunle and traditional Bale Baroka.",
                "options": [
                    ("A", "Sadiku", False),
                    ("B", "Sidi", True),
                    ("C", "Amope", False),
                    ("D", "Segi", False),
                    ("E", "Oya", False),
                ],
            },
            {
                "num": 2,
                "text": "Dramatic irony occurs when:",
                "explanation": "Dramatic irony happens when the audience or reader knows crucial facts of which the characters are unaware.",
                "options": [
                    ("A", "A character says the opposite of what they mean", False),
                    ("B", "The audience knows important information that a character is unaware of", True),
                    ("C", "The ending is unexpectedly happy", False),
                    ("D", "Two characters argue violently", False),
                    ("E", "A poem lacks rhyming scheme", False),
                ],
            },
            {
                "num": 3,
                "text": "A statement that seems self-contradictory on the surface but reveals a deeper underlying truth is a:",
                "explanation": "A paradox is a seemingly contradictory statement that exposes a profound truth.",
                "options": [
                    ("A", "Oxymoron", False),
                    ("B", "Paradox", True),
                    ("C", "Euphemism", False),
                    ("D", "Litotes", False),
                    ("E", "Hyperbole", False),
                ],
            },
            {
                "num": 4,
                "text": "In Shakespeare's tragedy 'Macbeth', which character's ghost appears at the royal banquet table to torment Macbeth?",
                "explanation": "The ghost of murdered Banquo sits in Macbeth's seat at the royal feast.",
                "options": [
                    ("A", "King Duncan", False),
                    ("B", "Banquo", True),
                    ("C", "Macduff", False),
                    ("D", "Malcolm", False),
                    ("E", "Lady Macbeth", False),
                ],
            },
            {
                "num": 5,
                "text": "The phrase 'cruel kindness' or 'deafening silence' is an example of:",
                "explanation": "An oxymoron juxtaposes two contradictory words side-by-side for rhetorical effect.",
                "options": [
                    ("A", "Simile", False),
                    ("B", "Oxymoron", True),
                    ("C", "Synecdoche", False),
                    ("D", "Metonymy", False),
                    ("E", "Apostrophe", False),
                ],
            },
        ],
    },
    "Commerce": {
        2022: [
            {
                "num": 1,
                "text": "Commerce is fundamentally defined as the study of:",
                "explanation": "Commerce encompasses trade and all aids to trade involved in distributing goods and services.",
                "options": [
                    ("A", "Banking and manufacturing only", False),
                    ("B", "Trade and all activities that facilitate the distribution of goods and services", True),
                    ("C", "Mining raw minerals", False),
                    ("D", "Agricultural farming methods", False),
                    ("E", "Government revenue collection", False),
                ],
            },
            {
                "num": 2,
                "text": "Which of the following is an 'Aid to Trade'?",
                "explanation": "Advertising, banking, communication, insurance, tourism, and warehousing are the primary aids to trade.",
                "options": [
                    ("A", "Extraction", False),
                    ("B", "Manufacturing", False),
                    ("C", "Warehousing", True),
                    ("D", "Farming", False),
                    ("E", "Fishing", False),
                ],
            },
            {
                "num": 3,
                "text": "The direct exchange of goods for other goods without the use of money is:",
                "explanation": "Barter trade is trade without a recognized monetary medium of exchange.",
                "options": [
                    ("A", "Hire purchase", False),
                    ("B", "Barter trade", True),
                    ("C", "Credit sales", False),
                    ("D", "Wholesale trade", False),
                    ("E", "Entrepot trade", False),
                ],
            },
            {
                "num": 4,
                "text": "A business organization owned, financed, and managed by one individual who bears all risks is a:",
                "explanation": "A sole proprietorship (one-man business) has single ownership and unlimited liability.",
                "options": [
                    ("A", "Partnership", False),
                    ("B", "Sole Proprietorship", True),
                    ("C", "Public Limited Company", False),
                    ("D", "Cooperative Society", False),
                    ("E", "Statutory Corporation", False),
                ],
            },
            {
                "num": 5,
                "text": "Which document is issued by a seller to a buyer to correct an undercharge on an invoice?",
                "explanation": "A debit note is sent to inform the buyer that their account has been debited (increasing amount owed).",
                "options": [
                    ("A", "Credit note", False),
                    ("B", "Debit note", True),
                    ("C", "Receipt", False),
                    ("D", "Delivery note", False),
                    ("E", "Pro-forma invoice", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "The minimum and maximum number of partners in an ordinary commercial partnership are:",
                "explanation": "Under standard partnership law, minimum members = 2, maximum members = 20 (or 10 for banking).",
                "options": [
                    ("A", "2 and 7", False),
                    ("B", "2 and 20", True),
                    ("C", "7 and 50", False),
                    ("D", "1 and 10", False),
                    ("E", "2 and unlimited", False),
                ],
            },
            {
                "num": 2,
                "text": "Which insurance principle states that the insured must stand to suffer a direct financial loss if the insured event occurs?",
                "explanation": "Insurable interest prevents gambling by requiring a legitimate financial stake in the subject matter.",
                "options": [
                    ("A", "Indemnity", False),
                    ("B", "Insurable Interest", True),
                    ("C", "Utmost Good Faith (Uberrimae Fidei)", False),
                    ("D", "Subrogation", False),
                    ("E", "Proximate Cause", False),
                ],
            },
            {
                "num": 3,
                "text": "A bonded warehouse is a specialized warehouse used for storing:",
                "explanation": "Bonded warehouses store dutiable imported goods under customs supervision until import tariffs are paid.",
                "options": [
                    ("A", "Perishable farm products", False),
                    ("B", "Dutiable imported goods on which customs duties have not yet been paid", True),
                    ("C", "Dangerous military ammunition", False),
                    ("D", "Expired medical drugs", False),
                    ("E", "Domestic postal parcels", False),
                ],
            },
            {
                "num": 4,
                "text": "Trade conducted between different independent nations of the world is called:",
                "explanation": "International / Foreign trade involves imports and exports across national borders.",
                "options": [
                    ("A", "Home trade", False),
                    ("B", "International (Foreign) trade", True),
                    ("C", "Retail trade", False),
                    ("D", "Wholesale trade", False),
                    ("E", "Regional market trade", False),
                ],
            },
            {
                "num": 5,
                "text": "The stock exchange market is a specialized capital market for buying and selling:",
                "explanation": "The stock exchange provides liquidity for trading existing securities (shares, stocks, bonds).",
                "options": [
                    ("A", "Second-hand motor cars", False),
                    ("B", "Shares, stocks, bonds, and securities", True),
                    ("C", "Raw agricultural foodstuff", False),
                    ("D", "Real estate land properties", False),
                    ("E", "Foreign currency cash only", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "The constitutional document that regulates a company's internal management, directors' powers, and voting rights is the:",
                "explanation": "Articles of Association govern the internal management and operations of a registered company.",
                "options": [
                    ("A", "Memorandum of Association", False),
                    ("B", "Articles of Association", True),
                    ("C", "Certificate of Incorporation", False),
                    ("D", "Prospectus", False),
                    ("E", "Trading Certificate", False),
                ],
            },
            {
                "num": 2,
                "text": "The insurance principle of 'Subrogation' ensures that:",
                "explanation": "Once the insurer fully indemnifies the insured, the insurer steps into the insured's shoes to claim against negligent third parties.",
                "options": [
                    ("A", "The insured can make a profit from insurance", False),
                    ("B", "The insurer assumes all legal rights of the insured against third parties after paying a claim", True),
                    ("C", "All policies are automatically cancelled yearly", False),
                    ("D", "Premiums must be paid in foreign currency", False),
                    ("E", "Only life insurance is valid", False),
                ],
            },
            {
                "num": 3,
                "text": "In modern e-commerce, the business model where an online firm sells products directly to individual end consumers is:",
                "explanation": "B2C stands for Business-to-Consumer e-commerce transactions.",
                "options": [
                    ("A", "B2B (Business-to-Business)", False),
                    ("B", "B2C (Business-to-Consumer)", True),
                    ("C", "C2C (Consumer-to-Consumer)", False),
                    ("D", "G2C (Government-to-Citizen)", False),
                    ("E", "B2G (Business-to-Government)", False),
                ],
            },
            {
                "num": 4,
                "text": "An 'Entrepot Trade' refers to:",
                "explanation": "Entrepot trade involves importing foreign goods for the purpose of re-exporting them to other countries.",
                "options": [
                    ("A", "Selling goods directly to retail consumers", False),
                    ("B", "Importing goods with the explicit intention of re-exporting them to other nations", True),
                    ("C", "Bartering raw commodities at sea ports", False),
                    ("D", "Trading exclusively inside free trade zones", False),
                    ("E", "Smuggling prohibited contraband", False),
                ],
            },
            {
                "num": 5,
                "text": "Which of the following describes a 'Debenture' in corporate finance?",
                "explanation": "A debenture is a long-term debt instrument acknowledging a loan to the company with fixed interest.",
                "options": [
                    ("A", "An equity share with voting power", False),
                    ("B", "A long-term loan certificate issued by a company with fixed interest repayment", True),
                    ("C", "A bank overdraft facility", False),
                    ("D", "A bonus dividend share", False),
                    ("E", "A commercial bill of exchange", False),
                ],
            },
        ],
    },
    "Agricultural Science": {
        2022: [
            {
                "num": 1,
                "text": "Which type of soil has the smallest particle size and highest water holding capacity?",
                "explanation": "Clay soil has particle sizes < 0.002 mm and retains water strongly.",
                "options": [
                    ("A", "Sandy soil", False),
                    ("B", "Loamy soil", False),
                    ("C", "Clay soil", True),
                    ("D", "Gravel", False),
                    ("E", "Silt", False),
                ],
            },
            {
                "num": 2,
                "text": "The primary macro-nutrients required in large quantities for healthy plant growth are:",
                "explanation": "Nitrogen (N), Phosphorus (P), and Potassium (K) are primary essential plant macro-nutrients.",
                "options": [
                    ("A", "Zinc, Boron, Copper", False),
                    ("B", "Nitrogen, Phosphorus, Potassium (N-P-K)", True),
                    ("C", "Iron, Manganese, Molybdenum", False),
                    ("D", "Calcium, Chlorine, Sodium", False),
                    ("E", "Lead, Nickel, Cobalt", False),
                ],
            },
            {
                "num": 3,
                "text": "The process of removing excess, weak, or unwanted seedlings from a stand to allow healthy growth is:",
                "explanation": "Thinning reduces seedling competition for light, space, moisture, and nutrients.",
                "options": [
                    ("A", "Mulching", False),
                    ("B", "Thinning", True),
                    ("C", "Pruning", False),
                    ("D", "Supplying", False),
                    ("E", "Weeding", False),
                ],
            },
            {
                "num": 4,
                "text": "A castrated male cattle is referred to as a:",
                "explanation": "Castrated male cattle is a steer or bullock; castrated male pig is a barrow; castrated chicken is a capon.",
                "options": [
                    ("A", "Bull", False),
                    ("B", "Steer (Bullock)", True),
                    ("C", "Heifer", False),
                    ("D", "Cow", False),
                    ("E", "Calf", False),
                ],
            },
            {
                "num": 5,
                "text": "Which of the following farm tools is primarily used for transplanting seedlings and digging small holes?",
                "explanation": "A hand trowel is designed for lifting seedlings and delicate transplanting operations.",
                "options": [
                    ("A", "Mattock", False),
                    ("B", "Hand trowel", True),
                    ("C", "Spade", False),
                    ("D", "Pickaxe", False),
                    ("E", "Sickle", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "The gestation period of a dairy cow (cattle) is approximately:",
                "explanation": "Cattle gestation averages about 280 to 285 days (~9 months).",
                "options": [
                    ("A", "114 days", False),
                    ("B", "150 days", False),
                    ("C", "283 days", True),
                    ("D", "336 days", False),
                    ("E", "30 days", False),
                ],
            },
            {
                "num": 2,
                "text": "Which livestock disease is caused by a protozoan transmitted by the Tsetse fly vector?",
                "explanation": "Trypanosomiasis (Nagana in cattle, sleeping sickness) is transmitted by Glossina (Tsetse flies).",
                "options": [
                    ("A", "Rinderpest", False),
                    ("B", "Anthrax", False),
                    ("C", "Trypanosomiasis", True),
                    ("D", "Foot and Mouth Disease", False),
                    ("E", "Brucellosis", False),
                ],
            },
            {
                "num": 3,
                "text": "Ruminant farm animals are characterized by having a four-compartment stomach consisting of:",
                "explanation": "The ruminant stomach consists of the Rumen (paunch), Reticulum (honeycomb), Omasum (manyplies), and Abomasum (true stomach).",
                "options": [
                    ("A", "Crop, Proventriculus, Gizzard, Caecum", False),
                    ("B", "Rumen, Reticulum, Omasum, Abomasum", True),
                    ("C", "Stomach, Liver, Gallbladder, Pancreas", False),
                    ("D", "Duodenum, Jejunum, Ileum, Colon", False),
                    ("E", "Pylorus, Cardia, Fundus, Caecum", False),
                ],
            },
            {
                "num": 4,
                "text": "The artificial application of water to soil for crop production during dry seasons is termed:",
                "explanation": "Irrigation supplies controlled water to agricultural lands during moisture deficits.",
                "options": [
                    ("A", "Drainage", False),
                    ("B", "Irrigation", True),
                    ("C", "Terracing", False),
                    ("D", "Contour bunding", False),
                    ("E", "Mulching", False),
                ],
            },
            {
                "num": 5,
                "text": "Which of the following is a leguminous cover crop widely used to improve soil nitrogen and prevent erosion?",
                "explanation": "Mucuna pruriens (velvet bean) and Centrosema are vigorous nitrogen-fixing cover legumes.",
                "options": [
                    ("A", "Zea mays (Maize)", False),
                    ("B", "Mucuna pruriens (Velvet bean)", True),
                    ("C", "Oryza sativa (Rice)", False),
                    ("D", "Manihot esculenta (Cassava)", False),
                    ("E", "Sorghum bicolor (Guinea corn)", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "The law of diminishing returns in agriculture states that as increasing variable inputs (e.g. fertilizer) are applied to a fixed plot of land:",
                "explanation": "Beyond an optimal point, each extra unit of input produces progressively smaller increments of yield.",
                "options": [
                    ("A", "Yield increases indefinitely without limit", False),
                    ("B", "Marginal yield will eventually decline", True),
                    ("C", "Total product immediately drops to zero", False),
                    ("D", "Costs become zero", False),
                    ("E", "The land becomes permanently sterile", False),
                ],
            },
            {
                "num": 2,
                "text": "In animal breeding, the mating of closely related individuals (e.g., sire to daughter or brother to sister) is known as:",
                "explanation": "Inbreeding concentrates desired homozygous traits but can lead to inbreeding depression.",
                "options": [
                    ("A", "Crossbreeding", False),
                    ("B", "Inbreeding", True),
                    ("C", "Outcrossing", False),
                    ("D", "Hybridization", False),
                    ("E", "Grading up", False),
                ],
            },
            {
                "num": 3,
                "text": "Which viral disease of poultry causes high mortality, respiratory distress, and twisted neck (torticollis)?",
                "explanation": "Newcastle disease is an acute, contagious viral infection in poultry controlled via vaccination.",
                "options": [
                    ("A", "Coccidiosis", False),
                    ("B", "Fowl typhoid", False),
                    ("C", "Newcastle disease", True),
                    ("D", "Aspergillosis", False),
                    ("E", "Fowl pox", False),
                ],
            },
            {
                "num": 4,
                "text": "The vegetative propagation method where a branch or stem is rooted while still attached to the parent plant is:",
                "explanation": "Layering (simple, air/marcotting) stimulates root formation before detaching the shoot.",
                "options": [
                    ("A", "Grafting", False),
                    ("B", "Budding", False),
                    ("C", "Layering", True),
                    ("D", "Stem cutting", False),
                    ("E", "Tissue culture", False),
                ],
            },
            {
                "num": 5,
                "text": "Which agricultural credit source provides formal, low-interest agricultural loans monitored by government policy?",
                "explanation": "Agricultural Development Banks and micro-credit institutions provide supervised agricultural financing.",
                "options": [
                    ("A", "Informal moneylenders", False),
                    ("B", "Bank of Agriculture / Agricultural Credit Guarantee Scheme", True),
                    ("C", "Village thrift contributors", False),
                    ("D", "Friends and relatives", False),
                    ("E", "Pawnbrokers", False),
                ],
            },
        ],
    },
    "Computer Studies": {
        2022: [
            {
                "num": 1,
                "text": "Which component of the Central Processing Unit (CPU) is responsible for performing arithmetic operations and logical comparisons?",
                "explanation": "The Arithmetic and Logic Unit (ALU) executes mathematical computations and decision-making logic.",
                "options": [
                    ("A", "Control Unit (CU)", False),
                    ("B", "Arithmetic and Logic Unit (ALU)", True),
                    ("C", "Registers", False),
                    ("D", "Cache memory", False),
                    ("E", "Bus interface", False),
                ],
            },
            {
                "num": 2,
                "text": "Which type of computer memory is volatile, meaning all its contents are lost when power is turned off?",
                "explanation": "RAM (Random Access Memory) is primary volatile memory that requires continuous power.",
                "options": [
                    ("A", "ROM", False),
                    ("B", "RAM", True),
                    ("C", "Hard Disk Drive", False),
                    ("D", "Flash drive", False),
                    ("E", "Optical disk", False),
                ],
            },
            {
                "num": 3,
                "text": "1 Gigabyte (GB) in binary data storage is equal to:",
                "explanation": "1 GB = 1024 Megabytes (MB) in standard binary computing notation.",
                "options": [
                    ("A", "1000 Kilobytes", False),
                    ("B", "1024 Kilobytes", False),
                    ("C", "1024 Megabytes (MB)", True),
                    ("D", "1000 Gigabits", False),
                    ("E", "1024 Terabytes", False),
                ],
            },
            {
                "num": 4,
                "text": "Which of the following is an example of system software?",
                "explanation": "An Operating System (e.g. Windows, Linux, macOS) manages system hardware and core software resources.",
                "options": [
                    ("A", "Microsoft Word", False),
                    ("B", "Microsoft Excel", False),
                    ("C", "Operating System (e.g., Linux, Windows)", True),
                    ("D", "CorelDRAW", False),
                    ("E", "VLC Media Player", False),
                ],
            },
            {
                "num": 5,
                "text": "The keyboard shortcut used to paste previously copied content into an application is:",
                "explanation": "Ctrl + V is the universal shortcut to paste clipboard content in Windows systems.",
                "options": [
                    ("A", "Ctrl + C", False),
                    ("B", "Ctrl + X", False),
                    ("C", "Ctrl + V", True),
                    ("D", "Ctrl + P", False),
                    ("E", "Ctrl + Z", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "In database management systems (DBMS), a unique field that uniquely identifies each individual record in a table is a:",
                "explanation": "A Primary Key enforces entity integrity by uniquely identifying each row in a database table.",
                "options": [
                    ("A", "Foreign key", False),
                    ("B", "Primary key", True),
                    ("C", "Composite key", False),
                    ("D", "Index pointer", False),
                    ("E", "Query parameter", False),
                ],
            },
            {
                "num": 2,
                "text": "Convert the decimal number 13 into binary (base 2):",
                "explanation": "13 in binary: 8 + 4 + 0 + 1 = 1101_2.",
                "options": [
                    ("A", "1011", False),
                    ("B", "1101", True),
                    ("C", "1110", False),
                    ("D", "1001", False),
                    ("E", "1111", False),
                ],
            },
            {
                "num": 3,
                "text": "Which network topology connects all nodes to a single central hub or switch device?",
                "explanation": "Star topology connects all network nodes to a central concentrator (hub or switch).",
                "options": [
                    ("A", "Bus topology", False),
                    ("B", "Ring topology", False),
                    ("C", "Star topology", True),
                    ("D", "Mesh topology", False),
                    ("E", "Tree topology", False),
                ],
            },
            {
                "num": 4,
                "text": "The communication protocol used for secure, encrypted data transmission across the World Wide Web is:",
                "explanation": "HTTPS (Hypertext Transfer Protocol Secure) encrypts web traffic using TLS/SSL.",
                "options": [
                    ("A", "FTP", False),
                    ("B", "HTTP", False),
                    ("C", "HTTPS", True),
                    ("D", "SMTP", False),
                    ("E", "DHCP", False),
                ],
            },
            {
                "num": 5,
                "text": "A malicious program designed to replicate itself across a computer network without human intervention is a:",
                "explanation": "A computer worm is self-replicating malware that spreads across network connections autonomously.",
                "options": [
                    ("A", "Trojan horse", False),
                    ("B", "Computer Worm", True),
                    ("C", "Spyware", False),
                    ("D", "Adware", False),
                    ("E", "Keylogger", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "In computer programming, the computational complexity Big-O notation for Binary Search on a sorted array is:",
                "explanation": "Binary search divides the search space in half at each step, yielding logarithmic time O(log n).",
                "options": [
                    ("A", "O(1)", False),
                    ("B", "O(log n)", True),
                    ("C", "O(n)", False),
                    ("D", "O(n log n)", False),
                    ("E", "O(n^2)", False),
                ],
            },
            {
                "num": 2,
                "text": "Which SQL statement is used to retrieve specific columns from a relational database table?",
                "explanation": "The SELECT statement retrieves specified attribute data from database tables.",
                "options": [
                    ("A", "UPDATE", False),
                    ("B", "INSERT", False),
                    ("C", "SELECT", True),
                    ("D", "DELETE", False),
                    ("E", "ALTER", False),
                ],
            },
            {
                "num": 3,
                "text": "In the OSI 7-layer networking model, which layer is responsible for logical IP addressing and routing packets?",
                "explanation": "The Network Layer (Layer 3) handles IP addressing, packet forwarding, and router routing protocols.",
                "options": [
                    ("A", "Physical Layer (Layer 1)", False),
                    ("B", "Data Link Layer (Layer 2)", False),
                    ("C", "Network Layer (Layer 3)", True),
                    ("D", "Transport Layer (Layer 4)", False),
                    ("E", "Application Layer (Layer 7)", False),
                ],
            },
            {
                "num": 4,
                "text": "Which cryptographic approach utilizes a pair of mathematically linked keys (public key and private key)?",
                "explanation": "Asymmetric (public-key) cryptography uses a public key for encryption and a private key for decryption.",
                "options": [
                    ("A", "Symmetric encryption", False),
                    ("B", "Asymmetric (Public-Key) encryption", True),
                    ("C", "Caesar cipher", False),
                    ("D", "MD5 hashing", False),
                    ("E", "Stream cipher", False),
                ],
            },
            {
                "num": 5,
                "text": "In object-oriented programming (OOP), the principle of bundling data and methods that operate on that data inside a single class unit is:",
                "explanation": "Encapsulation bundles data members and member functions together while hiding internal implementation.",
                "options": [
                    ("A", "Inheritance", False),
                    ("B", "Polymorphism", False),
                    ("C", "Encapsulation", True),
                    ("D", "Abstraction", False),
                    ("E", "Recursion", False),
                ],
            },
        ],
    },
    "Civic Education": {
        2022: [
            {
                "num": 1,
                "text": "Values that promote peaceful co-existence, honesty, and mutual respect in a society are known as:",
                "explanation": "Civic or moral values foster unity, respect, order, and positive social responsibility.",
                "options": [
                    ("A", "Negative values", False),
                    ("B", "Positive civic values", True),
                    ("C", "Feudal values", False),
                    ("D", "Anarchist values", False),
                    ("E", "Colonial values", False),
                ],
            },
            {
                "num": 2,
                "text": "A legal member of a state who enjoys constitutional rights, privileges, and owes allegiance is a:",
                "explanation": "A citizen enjoys full constitutional rights, duties, and reciprocal state protection.",
                "options": [
                    ("A", "Tourist", False),
                    ("B", "Citizen", True),
                    ("C", "Alien", False),
                    ("D", "Refugee", False),
                    ("E", "Diplomat", False),
                ],
            },
            {
                "num": 3,
                "text": "Which of the following is a civic responsibility of every law-abiding citizen?",
                "explanation": "Paying legitimate taxes, obeying statutory laws, and voting in elections are primary civic obligations.",
                "options": [
                    ("A", "Evading income tax", False),
                    ("B", "Payment of taxes and obedience to constitutional laws", True),
                    ("C", "Taking laws into one's hands", False),
                    ("D", "Vandalizing public infrastructure", False),
                    ("E", "Rigging national elections", False),
                ],
            },
            {
                "num": 4,
                "text": "The Universal Declaration of Human Rights (UDHR) was officially adopted by the United Nations General Assembly in:",
                "explanation": "The UN General Assembly proclaimed the UDHR in Paris on December 10, 1948.",
                "options": [
                    ("A", "1914", False),
                    ("B", "1945", False),
                    ("C", "1948", True),
                    ("D", "1960", False),
                    ("E", "1999", False),
                ],
            },
            {
                "num": 5,
                "text": "Which agency in Nigeria is primarily responsible for drug law enforcement and curbing narcotics abuse?",
                "explanation": "The National Drug Law Enforcement Agency (NDLEA) is mandated to eliminate illicit drug trafficking.",
                "options": [
                    ("A", "FRSC", False),
                    ("B", "NDLEA", True),
                    ("C", "EFCC", False),
                    ("D", "NAFDAC", False),
                    ("E", "ICPC", False),
                ],
            },
        ],
        2023: [
            {
                "num": 1,
                "text": "Cultism in educational institutions is hazardous primarily because it leads to:",
                "explanation": "Cultism breeds violence, armed intimidation, loss of innocent lives, and moral decay in academic institutions.",
                "options": [
                    ("A", "Academic excellence", False),
                    ("B", "Violence, insecurity, and destruction of lives", True),
                    ("C", "Community development", False),
                    ("D", "Promoting sportsmanship", False),
                    ("E", "Youth leadership empowerment", False),
                ],
            },
            {
                "num": 2,
                "text": "The agency responsible for ensuring road safety, highway orderliness, and issuing drivers' licenses in Nigeria is:",
                "explanation": "The Federal Road Safety Corps (FRSC) was established to prevent road crashes and enforce highway safety.",
                "options": [
                    ("A", "Nigeria Police Force", False),
                    ("B", "Federal Road Safety Corps (FRSC)", True),
                    ("C", "Civil Defence Corps (NSCDC)", False),
                    ("D", "Customs Service", False),
                    ("E", "Immigration Service", False),
                ],
            },
            {
                "num": 3,
                "text": "Political apathy can be effectively discouraged in a democracy by:",
                "explanation": "Public voter education, transparent electoral processes, and good governance encourage active civic participation.",
                "options": [
                    ("A", "Banning political parties", False),
                    ("B", "Massive voter education and transparent electoral processes", True),
                    ("C", "Harassing opposition leaders", False),
                    ("D", "Increasing election application fees", False),
                    ("E", "Imposing military curfews during voting", False),
                ],
            },
            {
                "num": 4,
                "text": "Which fundamental human right guarantees that a person cannot be detained indefinitely without trial?",
                "explanation": "The right to personal liberty guarantees fair hearing and prohibits unlawful, arbitrary detention.",
                "options": [
                    ("A", "Right to privacy", False),
                    ("B", "Right to personal liberty and fair hearing", True),
                    ("C", "Right to acquire property", False),
                    ("D", "Right to freedom of thought", False),
                    ("E", "Right to peaceful assembly", False),
                ],
            },
            {
                "num": 5,
                "text": "The anti-corruption agency in Nigeria charged with investigating financial crimes and economic fraud is the:",
                "explanation": "The Economic and Financial Crimes Commission (EFCC) investigates and prosecutes financial crimes in Nigeria.",
                "options": [
                    ("A", "INEC", False),
                    ("B", "EFCC", True),
                    ("C", "NHRC", False),
                    ("D", "NEMA", False),
                    ("E", "NOA", False),
                ],
            },
        ],
        2024: [
            {
                "num": 1,
                "text": "Democracy is famously characterized by Abraham Lincoln as the government:",
                "explanation": "Abraham Lincoln defined democracy as 'government of the people, by the people, for the people' in the Gettysburg Address.",
                "options": [
                    ("A", "Of the wealthy, by the military, for the state", False),
                    ("B", "Of the people, by the people, for the people", True),
                    ("C", "Of the monarch, by the nobles, for the subjects", False),
                    ("D", "Of the party, by the delegates, for the president", False),
                    ("E", "Of the church, by the clergy, for the congregation", False),
                ],
            },
            {
                "num": 2,
                "text": "The condition where citizens enjoy mutual trust, communal cohesion, and shared commitment to national development is:",
                "explanation": "National integration fosters unity across diverse ethnic, cultural, and religious groups.",
                "options": [
                    ("A", "Tribal chauvinism", False),
                    ("B", "National integration and social cohesion", True),
                    ("C", "Military dictatorship", False),
                    ("D", "Secessionist agitation", False),
                    ("E", "Feudal vassalage", False),
                ],
            },
            {
                "num": 3,
                "text": "Human trafficking violates fundamental human rights primarily because it involves:",
                "explanation": "Human trafficking constitutes modern slavery, forced labor, and severe exploitation of vulnerable persons.",
                "options": [
                    ("A", "Voluntary tourism", False),
                    ("B", "Forced labor, exploitation, and dehumanizing modern slavery", True),
                    ("C", "International exchange programs", False),
                    ("D", "Legal emigration through proper visas", False),
                    ("E", "Commercial trading of consumer goods", False),
                ],
            },
            {
                "num": 4,
                "text": "An autonomous national body responsible for conducting free and fair federal and state elections in Nigeria is:",
                "explanation": "INEC (Independent National Electoral Commission) organizes and supervises elections in Nigeria.",
                "options": [
                    ("A", "National Assembly", False),
                    ("B", "Independent National Electoral Commission (INEC)", True),
                    ("C", "Federal High Court", False),
                    ("D", "Ministry of Interior", False),
                    ("E", "National Orientation Agency", False),
                ],
            },
            {
                "num": 5,
                "text": "The National Orientation Agency (NOA) in Nigeria was established primarily to:",
                "explanation": "The NOA promotes civic enlightenment, patriotic values, and public awareness of government policies.",
                "options": [
                    ("A", "Enforce traffic regulations", False),
                    ("B", "Promote civic enlightenment, national unity, and positive civic values", True),
                    ("C", "Arrest economic smugglers", False),
                    ("D", "Print national currency notes", False),
                    ("E", "Control commodity market prices", False),
                ],
            },
        ],
    },
}


def run_seed():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("SEEDING ACADEMIC QUESTION BANK (10+ SUBJECTS x 3 CLASSES)")
    print("=" * 60)

    # 1. Initialize DB schema
    init_database()

    with SessionLocal() as db:
        # 2. Seed / ensure demo students
        print("\n1. Ensuring Demo Candidates for SS1, SS2, and SS3...")
        created_students = 0
        for st_data in STUDENTS_DATA:
            existing = db.query(User).filter(User.username == st_data["username"]).first()
            if not existing:
                u = User(
                    username=st_data["username"],
                    password="password123",
                    full_name=st_data["full_name"],
                    role=st_data["role"],
                    student_class=st_data["student_class"],
                    admission_year=st_data["admission_year"],
                    is_active=True,
                )
                db.add(u)
                created_students += 1
        db.commit()
        print(f"   [OK] Candidate seeding completed ({created_students} new students added).")

        # 3. Seed Subjects
        print("\n2. Seeding Academic Subjects...")
        subject_map = {}
        for s_data in SUBJECTS_DATA:
            subj = db.query(Subject).filter(Subject.name == s_data["name"]).first()
            if not subj:
                subj = Subject(
                    name=s_data["name"],
                    code=s_data["code"],
                    is_active=True,
                )
                db.add(subj)
                db.flush()
            subject_map[s_data["name"]] = subj
        db.commit()
        print(f"   [OK] {len(subject_map)} Subjects registered and active.")

        # 4. Seed Questions and Options
        print("\n3. Seeding Curated Questions and Options...")
        total_q_added = 0
        total_opt_added = 0

        for subj_name, years_data in QUESTIONS_BANK.items():
            subj_obj = subject_map.get(subj_name)
            if not subj_obj:
                continue

            for year, questions_list in years_data.items():
                for q_info in questions_list:
                    # Check if question already exists
                    existing_q = (
                        db.query(Question)
                        .filter(
                            Question.subject_id == subj_obj.id,
                            Question.year == year,
                            Question.question_number == q_info["num"],
                        )
                        .first()
                    )

                    if not existing_q:
                        new_q = Question(
                            subject_id=subj_obj.id,
                            year=year,
                            question_number=q_info["num"],
                            text=q_info["text"],
                            explanation=q_info["explanation"],
                            is_active=True,
                        )
                        db.add(new_q)
                        db.flush()
                        total_q_added += 1

                        # Add options
                        for pos, (lbl, opt_text, is_corr) in enumerate(q_info["options"], start=1):
                            opt = Option(
                                question_id=new_q.id,
                                label=lbl,
                                position=pos,
                                text=opt_text,
                                is_correct=is_corr,
                            )
                            db.add(opt)
                            total_opt_added += 1
                    else:
                        # Refresh question text & explanation if updated
                        existing_q.text = q_info["text"]
                        existing_q.explanation = q_info["explanation"]
                        existing_q.is_active = True

        db.commit()

        # 5. Summary statistics
        total_subjects = db.query(Subject).count()
        total_questions = db.query(Question).count()
        total_options = db.query(Option).count()
        distinct_years = [r[0] for r in db.query(Question.year).distinct().order_by(Question.year.asc()).all()]

        print("\n" + "=" * 60)
        print("SEEDING PROCESS COMPLETED SUCCESSFULLY!")
        print(f"   - Total Active Subjects:  {total_subjects}")
        print(f"   - Total Academic Years:   {distinct_years} (2022=SS1, 2023=SS2, 2024=SS3)")
        print(f"   - Total Questions in DB:  {total_questions}")
        print(f"   - Total Options in DB:    {total_options}")
        print(f"   - Newly Added Questions:  {total_q_added}")
        print(f"   - Newly Added Options:    {total_opt_added}")
        print("=" * 60)


if __name__ == "__main__":
    run_seed()
