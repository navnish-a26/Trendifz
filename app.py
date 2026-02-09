import os
import json
import random
import requests
import io
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# --- INITIALIZATION ---
load_dotenv()
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

MODEL_NAME = "gemini-1.5-flash-latest"

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"✅ Gemini API configured successfully with model: {MODEL_NAME}")
except Exception as e:
    model = None
    print(f"❌ CRITICAL: Failed to configure Gemini API. Error: {e}")

IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")
IMGFLIP_API_URL = "https://api.imgflip.com/caption_image"

# --- DATABASES ---
TRENDING_TOPICS = [
    {"name": "Taylor Swift's engagement"},
    {"name": "Demon Slayer Infinity Castle"},
    {"name": "Attack on titan"},
    {"name": "Vote Scam India"},
    {"name": "Global climate change summit"},
    {"name": "Recent viral video challenges"},
]

MEMES_DATA = [
    {"id": "112126428", "name": "Distracted Boyfriend", "description": "A man looking at another woman while his girlfriend looks on disapprovingly.", "box_count": 3, "base_url": "https://i.imgflip.com/1ur9b0.jpg"},
    {"id": "438680", "name": "Batman Slapping Robin", "description": "Batman slapping Robin, often used to correct a foolish statement.", "box_count": 2, "base_url": "https://i.imgflip.com/9ehk.jpg"},
    {"id": "87743020", "name": "Two Buttons", "description": "A character sweating while trying to choose between two buttons, representing a difficult choice.", "box_count": 2, "base_url": "https://i.imgflip.com/1g8my4.jpg"},
    {"id": "181913649", "name": "Drake Hotline Bling", "description": "Drake looking displeased at one option and pleased at another.", "box_count": 2, "base_url": "https://i.imgflip.com/30b1gx.jpg"},
    {"id": "61579", "name": "One Does Not Simply", "description": "Boromir from Lord of the Rings explaining a task is harder than it seems.", "box_count": 2, "base_url": "https://i.imgflip.com/1b42.jpg"},
    {"id": "102156234", "name": "Mocking Spongebob", "description": "Spongebob making a mocking face, used to repeat someone's words sarcastically.", "box_count": 2, "base_url": "https://i.imgflip.com/1otk96.jpg"},
    {"id": "93895088", "name": "Expanding Brain", "description": "Images showing an increasingly enlightened or absurd state of mind.", "box_count": 4, "base_url": "https://i.imgflip.com/1jwhww.jpg"},
    {"id": "129242436", "name": "Change My Mind", "description": "Steven Crowder at a table with a sign, inviting debate on a controversial topic.", "box_count": 2, "base_url": "https://i.imgflip.com/24y43o.jpg"},
    {"id": "124822590", "name": "Left Exit 12 Off Ramp", "description": "A car swerving dramatically to take an off-ramp, representing a sudden, decisive choice.", "box_count": 3, "base_url": "https://i.imgflip.com/22bdq6.jpg"},
    {"id": "101470", "name": "Ancient Aliens", "description": "Giorgio Tsoukalos suggesting aliens are the explanation for a phenomenon.", "box_count": 2, "base_url": "https://i.imgflip.com/26am.jpg"},
    {"id": "89370399", "name": "Roll Safe Think About It", "description": "A man pointing to his head, offering questionable but technically logical advice.", "box_count": 2, "base_url": "https://i.imgflip.com/1h7in3.jpg"},
    {"id": "188390779", "name": "Woman Yelling at a Cat", "description": "A woman yelling emotionally at a calm cat sitting at a dinner table.", "box_count": 2, "base_url": "https://i.imgflip.com/32hp9x.jpg"},
    {"id": "155067746", "name": "Surprised Pikachu", "description": "Pikachu with a shocked expression, used when a predictable outcome occurs.", "box_count": 2, "base_url": "https://i.imgflip.com/2kbn1e.jpg"},
    {"id": "91538330", "name": "This Is Fine", "description": "A dog sitting in a burning room, calmly saying 'This is fine.'", "box_count": 2, "base_url": "https://i.imgflip.com/1pp521.jpg"},
    {"id": "1035805", "name": "Boardroom Meeting Suggestion", "description": "An employee's good suggestion gets him thrown out of a window by executives.", "box_count": 3, "base_url": "https://i.imgflip.com/26jxv.jpg"},
    {"id": "217743513", "name": "UNO Draw 25 Cards", "description": "A person choosing to draw 25 cards in UNO rather than perform an undesirable action.", "box_count": 2, "base_url": "https://i.imgflip.com/3lmzyx.jpg"},
    {"id": "119139145", "name": "Gru's Plan", "description": "A four-panel comic where Gru's plan has an unexpected and negative final step.", "box_count": 4, "base_url": "https://i.imgflip.com/1u1vo7.jpg"},
    {"id": "247375501", "name": "Buff Doge vs. Cheems", "description": "A strong, buff Doge compared to a small, weak Cheems, representing superiority vs. inferiority.", "box_count": 2, "base_url": "https://i.imgflip.com/43a45p.jpg"},
    {"id": "131087935", "name": "Running Away Balloon", "description": "A character letting go of one balloon (a problem) to chase another (a bigger problem).", "box_count": 3, "base_url": "https://i.imgflip.com/265h4.jpg"},
    {"id": "97984", "name": "Disaster Girl", "description": "A little girl smiling devilishly in front of a burning house.", "box_count": 2, "base_url": "https://i.imgflip.com/23ls.jpg"},
    {"id": "100777631", "name": "Is This a Pigeon?", "description": "An anime character naively misidentifying something obvious.", "box_count": 3, "base_url": "https://i.imgflip.com/1o00in.jpg"},
    {"id": "135256802", "name": "Epic Handshake", "description": "Two muscular arms clasping in an epic handshake, representing a powerful agreement.", "box_count": 3, "base_url": "https://i.imgflip.com/28j0te.jpg"},
    {"id": "178591752", "name": "Tuxedo Winnie The Pooh", "description": "Comparing a simple or crude thing (regular Pooh) to a sophisticated one (tuxedo Pooh).", "box_count": 2, "base_url": "https://i.imgflip.com/2ybua0.jpg"},
    {"id": "222403160", "name": "Bernie I Am Once Again Asking For Your Support", "description": "Bernie Sanders asking for financial support, used for humorous requests.", "box_count": 2, "base_url": "https://i.imgflip.com/3o5s8a.jpg"},
    {"id": "161865971", "name": "Marked Safe From", "description": "Using Facebook's 'Marked Safe' feature for trivial or unrelatable things.", "box_count": 1, "base_url": "https://i.imgflip.com/2odckz.jpg"},
    {"id": "148909805", "name": "Monkey Puppet", "description": "A puppet looking away awkwardly, representing an uncomfortable or tense situation.", "box_count": 2, "base_url": "https://i.imgflip.com/2gnnjh.jpg"},
    {"id": "27813981", "name": "Hide the Pain Harold", "description": "An elderly man smiling while looking uncomfortable, masking pain or distress.", "box_count": 2, "base_url": "https://i.imgflip.com/8p4j.jpg"},
    {"id": "4087833", "name": "Waiting Skeleton", "description": "A skeleton waiting on a bench, representing a very long wait for something.", "box_count": 2, "base_url": "https://i.imgflip.com/2fm6x.jpg"},
    {"id": "131940431", "name": "Gru's Plan", "description": "A four-panel comic showing a plan with an unexpected and usually bad final step.", "box_count": 4, "base_url": "https://i.imgflip.com/1u1vo7.jpg"},
    {"id": "79132341", "name": "Bike Fall", "description": "A person putting a stick in their own bicycle wheel, representing self-sabotage.", "box_count": 3, "base_url": "https://i.imgflip.com/1f3mnm.jpg"},
    {"id": "61544", "name": "Success Kid", "description": "A baby clenching his fist in a determined way, celebrating a small victory.", "box_count": 2, "base_url": "https://i.imgflip.com/1b41.jpg"},
    {"id": "110163934", "name": "I Bet He's Thinking About Other Women", "description": "A woman in bed thinking her partner is thinking of other women, while he's thinking of something absurd.", "box_count": 2, "base_url": "https://i.imgflip.com/1tl71a.jpg"},
    {"id": "132769734", "name": "Hard To Swallow Pills", "description": "A bottle of pills labeled with a truth that is difficult to accept.", "box_count": 1, "base_url": "https://i.imgflip.com/271ps6.jpg"},
    {"id": "61520", "name": "Futurama Fry", "description": "Fry from Futurama squinting suspiciously, used for 'not sure if X or Y' jokes.", "box_count": 2, "base_url": "https://i.imgflip.com/1b0.jpg"},
    {"id": "5496396", "name": "Scumbag Steve", "description": "A man with a sideways hat, representing a selfish or inconsiderate person.", "box_count": 2, "base_url": "https://i.imgflip.com/32g5.jpg"},
    {"id": "195515965", "name": "Clown Applying Makeup", "description": "A clown applying makeup, representing someone getting ready to do something foolish.", "box_count": 4, "base_url": "https://i.imgflip.com/38el31.jpg"},
    {"id": "226297822", "name": "Panik Kalm Panik", "description": "A three-panel meme showing a character panicking, calming down, and then panicking again.", "box_count": 3, "base_url": "https://i.imgflip.com/3qq3qc.jpg"},
    {"id": "80707627", "name": "Sad Pablo Escobar", "description": "Pablo Escobar staring blankly, representing a moment of deep, lonely thought or sadness.", "box_count": 3, "base_url": "https://i.imgflip.com/1f98pi.jpg"},
    {"id": "114585183", "name": "Inhaling Seagull", "description": "A seagull inhaling deeply, used to represent preparing for a long rant or a big statement.", "box_count": 2, "base_url": "https://i.imgflip.com/1w7ygt.jpg"},
    {"id": "322841254", "name": "Trade Offer", "description": "A man offering a trade, usually where one side gets a much better deal.", "box_count": 2, "base_url": "https://i.imgflip.com/54h64r.jpg"},
    {"id": "252600902", "name": "Always Has Been", "description": "Two astronauts in space, where one reveals a surprising truth to the other.", "box_count": 2, "base_url": "https://i.imgflip.com/46e43q.jpg"},
    {"id": "177682295", "name": "You Guys Are Getting Paid?", "description": "A character from 'We're the Millers' looking surprised that others are getting paid for something he does for free.", "box_count": 2, "base_url": "https://i.imgflip.com/2xscjb.jpg"},
    {"id": "309868305", "name": "Anakin Padme 4 Panel", "description": "A four-panel comic with Anakin and Padme, where Padme's silence represents a shocking realization.", "box_count": 4, "base_url": "https://i.imgflip.com/4y8x5d.jpg"},
    {"id": "84341851", "name": "I'm Something Of A Scientist Myself", "description": "Willem Dafoe as the Green Goblin, used to boast about minor expertise.", "box_count": 2, "base_url": "https://i.imgflip.com/1f5202.jpg"},
    {"id": "123999232", "name": "The Scroll Of Truth", "description": "A character finding a scroll that reveals an unpleasant truth.", "box_count": 2, "base_url": "https://i.imgflip.com/21t5my.jpg"},
    {"id": "216951317", "name": "Guy Holding Cardboard Sign", "description": "A man protesting with a sign, used to express a strong or unpopular opinion.", "box_count": 1, "base_url": "https://i.imgflip.com/3l5l52.jpg"},
    {"id": "134797956", "name": "They're The Same Picture", "description": "Pam from 'The Office' being shown two different pictures and saying they are the same.", "box_count": 2, "base_url": "https://i.imgflip.com/28s2gu.jpg"},
    {"id": "28251713", "name": "Oprah You Get A", "description": "Oprah Winfrey generously giving something to everyone in her audience.", "box_count": 2, "base_url": "https://i.imgflip.com/8k03.jpg"},
    {"id": "135678846", "name": "Who Killed Hannibal", "description": "A character asking who did something, while the culprit is obvious in the background.", "box_count": 2, "base_url": "https://i.imgflip.com/28s2gu.jpg"},
    {"id": "259237855", "name": "Laughing Leo", "description": "Leonardo DiCaprio laughing while holding a drink, used to mock a situation.", "box_count": 2, "base_url": "https://i.imgflip.com/46e43q.jpg"},
    {"id": "19665182", "name": "I'm The Captain Now", "description": "A character from 'Captain Phillips' declaring his new authority.", "box_count": 2, "base_url": "https://i.imgflip.com/4t0.jpg"},
    {"id": "101288", "name": "Third World Success Kid", "description": "A dancing child celebrating a minor success in a third-world context.", "box_count": 2, "base_url": "https://i.imgflip.com/1b7q.jpg"},
    {"id": "101956", "name": "Yo Dawg Heard You", "description": "Xzibit explaining a recursive concept, like putting a thing inside the same thing.", "box_count": 2, "base_url": "https://i.imgflip.com/1b8f.jpg"},
    {"id": "8072285", "name": "Doge", "description": "The Shiba Inu dog, surrounded by colorful Comic Sans text representing internal monologue.", "box_count": 2, "base_url": "https://i.imgflip.com/4t0.jpg"},
    {"id": "124055727", "name": "Y'all Got Any More Of That", "description": "A character from 'Chappelle's Show' frantically scratching his neck, asking for more of something.", "box_count": 2, "base_url": "https://i.imgflip.com/21uy0f.jpg"},
    {"id": "14230520", "name": "Black Girl Wat", "description": "A girl with a confused expression, representing bewilderment.", "box_count": 2, "base_url": "https://i.imgflip.com/2n25.jpg"},
    {"id": "61585", "name": "Bad Luck Brian", "description": "A nerdy-looking teenager in a series of unfortunate situations.", "box_count": 2, "base_url": "https://i.imgflip.com/1b52.jpg"},
    {"id": "6531067", "name": "The Most Interesting Man In The World", "description": "A sophisticated man stating something he doesn't always do, but when he does, it's interesting.", "box_count": 2, "base_url": "https://i.imgflip.com/3g2.jpg"},
    {"id": "40945639", "name": "Dr Evil Laser", "description": "Dr. Evil making air quotes to sarcastically describe something.", "box_count": 2, "base_url": "https://i.imgflip.com/wz56.jpg"},
    {"id": "21735", "name": "The Rock Driving", "description": "Dwayne 'The Rock' Johnson looking back from the driver's seat with a concerned expression.", "box_count": 2, "base_url": "https://i.imgflip.com/1b4j.jpg"},
    {"id": "29617627", "name": "Look At Me", "description": "A character from 'Captain Phillips' asserting dominance or importance.", "box_count": 2, "base_url": "https://i.imgflip.com/98s.jpg"},
    {"id": "14371066", "name": "Star Wars Yoda", "description": "Yoda offering wise or insightful advice.", "box_count": 2, "base_url": "https://i.imgflip.com/2o5d.jpg"},
    {"id": "61532", "name": "Good Guy Greg", "description": "A friendly-looking man representing considerate and kind behavior.", "box_count": 2, "base_url": "https://i.imgflip.com/1b2d.jpg"},
    {"id": "563423", "name": "That Would Be Great", "description": "Bill Lumbergh from 'Office Space' passively-aggressively asking an employee to do something.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"},
    {"id": "28034788", "name": "Marvel Civil War 1", "description": "Captain America and Iron Man facing off, representing two opposing sides of a debate.", "box_count": 2, "base_url": "https://i.imgflip.com/8k03.jpg"},
    {"id": "92214351", "name": "Laughing Men In Suits", "description": "Men in suits laughing hysterically, often at a ridiculous or naive idea.", "box_count": 2, "base_url": "https://i.imgflip.com/1h5c27.jpg"},
    {"id": "101716", "name": "Grumpy Cat", "description": "A cat with a perpetually grumpy expression, used for cynical or negative comments.", "box_count": 2, "base_url": "https://i.imgflip.com/1b6t.jpg"},
    {"id": "4173692", "name": "Joseph Ducreux", "description": "A self-portrait of Joseph Ducreux, used to rephrase modern song lyrics in an archaic way.", "box_count": 2, "base_url": "https://i.imgflip.com/2g60.jpg"},
    {"id": "120235", "name": "Matrix Morpheus", "description": "Morpheus from 'The Matrix' presenting a mind-bending proposition.", "box_count": 2, "base_url": "https://i.imgflip.com/1b1a.jpg"},
    {"id": "29562797", "name": "I'll Just Wait Here", "description": "A skeleton waiting at a table, implying a very long wait.", "box_count": 2, "base_url": "https://i.imgflip.com/98s.jpg"},
    {"id": "77045868", "name": "Afraid To Ask Andy", "description": "Andy Dwyer from 'Parks and Rec' being too afraid to ask about a topic he doesn't understand.", "box_count": 2, "base_url": "https://i.imgflip.com/1e7ql7.jpg"},
    {"id": "1367068", "name": "I Should Buy A Boat Cat", "description": "A cat looking thoughtfully out a window, representing a sudden, life-changing realization or purchase idea.", "box_count": 2, "base_url": "https://i.imgflip.com/2bg6.jpg"},
    {"id": "24557067", "name": "Spongebob Ight Imma Head Out", "description": "Spongebob getting up to leave, used when exiting an awkward or undesirable situation.", "box_count": 2, "base_url": "https://i.imgflip.com/8k03.jpg"},
    {"id": "8279514", "name": "Evil Toddler", "description": "A toddler with a mischievous look, representing a diabolical or evil plan.", "box_count": 2, "base_url": "https://i.imgflip.com/4t0.jpg"},
    {"id": "99683372", "name": "Sleeping Shaq", "description": "Comparing a calm state (Sleeping Shaq) to an energetic one (Woke Shaq).", "box_count": 2, "base_url": "https://i.imgflip.com/1nck6k.jpg"},
    {"id": "175540455", "name": "Nobody:", "description": "A preface to show that someone is offering an unsolicited or random opinion.", "box_count": 1, "base_url": "https://i.imgflip.com/2v7w7a.jpg"},
    {"id": "61581", "name": "Creepy Condescending Wonka", "description": "Willy Wonka looking condescendingly, used for sarcastic questions.", "box_count": 2, "base_url": "https://i.imgflip.com/1b4f.jpg"},
    {"id": "371382", "name": "Simba Shadowy Place", "description": "Mufasa telling Simba not to go to a dangerous place, representing a forbidden area or topic.", "box_count": 2, "base_url": "https://i.imgflip.com/9ehk.jpg"},
    {"id": "405658", "name": "Grinds My Gears", "description": "Peter Griffin from 'Family Guy' explaining what annoys him.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"},
    {"id": "221578498", "name": "Grant Gustin over grave", "description": "Grant Gustin smiling and giving a peace sign over a grave, representing a positive outcome after something has ended.", "box_count": 2, "base_url": "https://i.imgflip.com/3nxk2j.jpg"},
    {"id": "101511", "name": "Don't You Squidward", "description": "Squidward looking nervously out a window, representing anxiety or paranoia.", "box_count": 2, "base_url": "https://i.imgflip.com/1b7q.jpg"},
    {"id": "101287", "name": "Unhelpful High School Teacher", "description": "A teacher offering unhelpful advice to a struggling student.", "box_count": 2, "base_url": "https://i.imgflip.com/1b7q.jpg"},
    {"id": "176908", "name": "Successfull Black Man", "description": "A well-dressed man looking pleased, representing a surprising or impressive achievement.", "box_count": 2, "base_url": "https://i.imgflip.com/1b4j.jpg"},
    {"id": "135232", "name": "First World Problems", "description": "A woman crying, representing a trivial complaint or inconvenience in a developed country.", "box_count": 2, "base_url": "https://i.imgflip.com/1b1a.jpg"},
    {"id": "252758727", "name": "Mother Ignoring Kid Drowning In A Pool", "description": "A mother ignoring her drowning child in favor of another, representing misplaced priorities.", "box_count": 3, "base_url": "https://i.imgflip.com/46e43q.jpg"},
    {"id": "180190441", "name": "They Don't Know", "description": "A character at a party thinking about their unique or secret knowledge.", "box_count": 2, "base_url": "https://i.imgflip.com/2v7w7a.jpg"},
    {"id": "224015", "name": "College Freshman", "description": "A young student representing naive or stereotypical freshman behavior.", "box_count": 2, "base_url": "https://i.imgflip.com/1b4j.jpg"},
    {"id": "110133729", "name": "I Love Democracy", "description": "Palpatine from 'Star Wars' saying 'I love democracy,' often used sarcastically.", "box_count": 2, "base_url": "https://i.imgflip.com/1tl71a.jpg"},
    {"id": "12403754", "name": "Bad Pun Dog", "description": "A dog telling a bad joke and looking pleased with itself.", "box_count": 3, "base_url": "https://i.imgflip.com/2n25.jpg"},
    {"id": "195389", "name": "Sparta Leonidas", "description": "Leonidas from the movie '300' yelling 'This is Sparta!'", "box_count": 2, "base_url": "https://i.imgflip.com/4t0.jpg"},
    {"id": "766986", "name": "Aaaaand Its Gone", "description": "A South Park banker character explaining that something valuable has suddenly disappeared.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"},
    {"id": "100955", "name": "Confession Bear", "description": "A bear looking sad, used to confess a controversial opinion or action.", "box_count": 2, "base_url": "https://i.imgflip.com/1b7q.jpg"},
    {"id": "444501", "name": "Maury Lie Detector", "description": "Maury Povich revealing that a lie detector test has confirmed a statement was a lie.", "box_count": 2, "base_url": "https://i.imgflip.com/9ehk.jpg"},
    {"id": "718432", "name": "Back In My Day", "description": "An old man complaining about how things were different or harder in the past.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"},
    {"id": "21604248", "name": "Mugatu So Hot Right Now", "description": "Mugatu from 'Zoolander' sarcastically remarking on a trend's popularity.", "box_count": 2, "base_url": "https://i.imgflip.com/4t0.jpg"},
    {"id": "124212", "name": "Say That Again I Dare You", "description": "Samuel L. Jackson from 'Pulp Fiction' looking intimidating.", "box_count": 2, "base_url": "https://i.imgflip.com/2n25.jpg"},
    {"id": "3218037", "name": "This Is Where I'd Put My Trophy If I Had One", "description": "A character from 'The Fairly OddParents' lamenting a lack of achievement.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"},
    {"id": "61583", "name": "Conspiracy Keanu", "description": "Keanu Reeves looking shocked, used for pseudo-profound or conspiratorial thoughts.", "box_count": 2, "base_url": "https://i.imgflip.com/1b4f.jpg"},
    {"id": "13757816", "name": "Awkward Moment Sealion", "description": "A sealion interjecting itself into a conversation, representing an awkward social situation.", "box_count": 2, "base_url": "https://i.imgflip.com/2n25.jpg"},
    {"id": "143601", "name": "Steve Harvey", "description": "Steve Harvey with a shocked or disappointed expression.", "box_count": 2, "base_url": "https://i.imgflip.com/2n25.jpg"},
    {"id": "163573", "name": "Imagination Spongebob", "description": "Spongebob making a rainbow with his hands, sarcastically used to say 'nobody cares.'", "box_count": 2, "base_url": "https://i.imgflip.com/1b7q.jpg"},
    {"id": "460541", "name": "Jack Sparrow Being Chased", "description": "Jack Sparrow running away from a large group of people.", "box_count": 2, "base_url": "https://i.imgflip.com/9ehk.jpg"},
    {"id": "442575", "name": "Ain't Nobody Got Time For That", "description": "Sweet Brown emphatically stating she doesn't have time for a particular situation.", "box_count": 2, "base_url": "https://i.imgflip.com/9ehk.jpg"},
    {"id": "1790995", "name": "And everybody loses their minds", "description": "The Joker from 'The Dark Knight' describing a chaotic public reaction.", "box_count": 2, "base_url": "https://i.imgflip.com/2670.jpg"}
]


# --- HELPER FUNCTIONS ---
def get_ai_response(prompt):
    if not model:
        raise Exception("AI model is not available.")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API Error: {e}")

def get_meme_by_id(template_id):
    return next((meme for meme in MEMES_DATA if meme['id'] == template_id), None)

# --- API ROUTES ---

@app.route('/api/lucky', methods=['POST'])
def lucky_generate():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "No topic provided."}), 400
    
    topic = data['topic']
    try:
        meme_options_text = "\n".join([f"- {meme['name']}: {meme['description']}" for meme in MEMES_DATA])
        template_prompt = f"Choose the single most appropriate meme template for the topic '{topic}' from this list:\n{meme_options_text}\n\nYour answer must be ONLY the name of the meme template, spelled exactly."
        
        selected_template_name = get_ai_response(template_prompt)
        selected_meme = next((meme for meme in MEMES_DATA if meme['name'].lower() == selected_template_name.lower()), None)
        if not selected_meme:
            selected_meme = random.choice(MEMES_DATA) # Fallback

        caption_prompt = f"Create text for the '{selected_meme['name']}' meme which has {selected_meme['box_count']} text boxes. The topic is '{topic}'. Your response must be a valid JSON array of strings. Example: [\"Text 1\", \"Text 2\"]"
        
        cleaned_json_text = get_ai_response(caption_prompt).replace("```json", "").replace("```", "")
        captions = json.loads(cleaned_json_text)

        response_data = {
            "template": selected_meme,
            "captions": captions
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Error in /lucky: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_templates():
    data = request.get_json()
    if not data or 'topic' not in data:
        return jsonify({"error": "No topic provided."}), 400
        
    topic = data['topic']
    try:
        meme_options_text = "\n".join([f"- {meme['name']}: {meme['description']}" for meme in MEMES_DATA])
        template_prompt = f"Choose the top 5 most relevant meme templates for the topic '{topic}' from this list:\n{meme_options_text}\n\nYour response must be a valid JSON array of the 5 exact template names. Example: [\"Name 1\", \"Name 2\", \"Name 3\", \"Name 4\", \"Name 5\"]"
        
        cleaned_json_text = get_ai_response(template_prompt).replace("```json", "").replace("```", "")
        selected_names = json.loads(cleaned_json_text)
        
        results = []
        for name in selected_names:
            found_meme = next((meme for meme in MEMES_DATA if meme['name'].lower() == name.lower()), None)
            if found_meme:
                results.append(found_meme)

        return jsonify(results)
    except Exception as e:
        print(f"❌ Error in /search: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/caption', methods=['POST'])
def generate_caption_for_template():
    data = request.get_json()
    if not data or 'topic' not in data or 'template_id' not in data:
        return jsonify({"error": "Missing topic or template_id."}), 400
    
    topic = data['topic']
    template_id = data['template_id']
    selected_meme = get_meme_by_id(template_id)

    if not selected_meme:
        return jsonify({"error": "Template not found."}), 404

    try:
        caption_prompt = f"Create text for the '{selected_meme['name']}' meme which has {selected_meme['box_count']} text boxes. The topic is '{topic}'. Your response must be a valid JSON array of strings. Example: [\"Text 1\", \"Text 2\"]"
        
        cleaned_json_text = get_ai_response(caption_prompt).replace("```json", "").replace("```", "")
        captions = json.loads(cleaned_json_text)
        
        response_data = {
            "template": selected_meme,
            "captions": captions
        }
        return jsonify(response_data)
    except Exception as e:
        print(f"❌ Error in /caption: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/customize', methods=['POST'])
def customize_meme():
    if not IMGFLIP_USERNAME or not IMGFLIP_PASSWORD:
        return jsonify({"error": "Imgflip credentials not set."}), 503

    data = request.get_json()
    if 'template_id' not in data or 'texts' not in data:
        return jsonify({"error": "Missing template_id or texts."}), 400

    payload = {
        'template_id': data['template_id'],
        'username': IMGFLIP_USERNAME,
        'password': IMGFLIP_PASSWORD,
    }
    for i, text in enumerate(data['texts']):
        payload[f'boxes[{i}][text]'] = text

    try:
        response = requests.post(IMGFLIP_API_URL, data=payload)
        response_data = response.json()
        if not response_data.get("success"):
            raise Exception(response_data.get('error_message', 'Unknown Imgflip error'))
        return jsonify({"url": response_data["data"]["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending_topics():
    return jsonify(TRENDING_TOPICS)

# --- NEW: Universal Image Proxy Endpoint ---
@app.route('/api/proxy')
def proxy_image():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided."}), 400
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        
        return send_file(
            io.BytesIO(response.content),
            mimetype=content_type
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching image from {url}: {e}")
        return jsonify({"error": "Failed to fetch image."}), 502
    except Exception as e:
        print(f"❌ Error in image proxy: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

# --- Serve Frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))

