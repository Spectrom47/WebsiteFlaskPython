import os
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

COMMENTS_FILE = "comments.json"
LIKES_FILE = "like_comment.json"

# =========================
# Helpers to load/save comments
# =========================
def load_comments():
    if not os.path.exists(COMMENTS_FILE):
        return []
    with open(COMMENTS_FILE, "r") as f:
        return json.load(f)

def save_comments(comments):
    with open(COMMENTS_FILE, "w") as f:
        json.dump(comments, f, indent=2)

# =========================
# Helpers to load/save likes
# =========================
def load_likes():
    if not os.path.exists(LIKES_FILE):
        return {}
    with open(LIKES_FILE, "r") as f:
        likes = json.load(f)
    if isinstance(likes, list):
        # Convert old list format to empty dict
        likes = {}
    return likes


def save_likes(likes):
    with open(LIKES_FILE, "w") as f:
        json.dump(likes, f, indent=2)

def get_likes_count(comment_id):
    likes = load_likes()
    return len(likes.get(str(comment_id), []))

def toggle_like(comment_id, user_id):
    likes = load_likes()
    cid = str(comment_id)
    if cid not in likes:
        likes[cid] = []
    if user_id in likes[cid]:
        likes[cid].remove(user_id)
    else:
        likes[cid].append(user_id)
    save_likes(likes)
    return len(likes[cid])

# =========================
# Context processor
# =========================
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    comments = load_comments()
    # Add likes count for each comment
    for c in comments:
        c["likes"] = get_likes_count(c["id"])
    return render_template("about.html", comments=comments)

@app.route("/projects")
def projects():
    # Map each tab to a list of photos instead of a single string
    tab_images = {
        "website": ["images/projects/photo-one.png"],
        "roblox": ["images/projects/photo-two.png"],
        "content": [
            "images/projects/photo-three.png",
            "images/projects/photo-five.png",
            "images/projects/photo-six.png"
        ],
        "misc": ["images/projects/photo-four.png"]
    }
    return render_template("projects.html", **tab_images)







@app.route("/contact")
def contact():
    return render_template("contact.html")

# =========================
# API Endpoints
# =========================
@app.route("/add_comment", methods=["POST"])
def add_comment():
    comments = load_comments()
    data = request.get_json()
    new_id = max([c["id"] for c in comments], default=0) + 1
    new_comment = {
        "id": new_id,
        "text": data["text"]
    }
    comments.append(new_comment)
    save_comments(comments)
    return jsonify({**new_comment, "likes": 0})

@app.route("/like_comment", methods=["POST"])
def like_comment():
    data = request.get_json()
    comment_id = data.get("id")
    user_id = request.remote_addr  # Can also use session/user login ID
    new_likes_count = toggle_like(comment_id, user_id)
    return jsonify({"likes": new_likes_count})

# =========================
# Run App
# =========================
if __name__ == "__main__":
    app.run(debug=True)
