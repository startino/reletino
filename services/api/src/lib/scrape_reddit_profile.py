from pydantic import BaseModel
from praw.models import Redditor
from src.interfaces.reddit import get_reddit_instance
from datetime import datetime
import json
import os

from src.models.profile import RedditUserProfile



def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def format_profile_for_llm(profile: RedditUserProfile) -> str:
    """
    Format the profile for a LLM.
    - Remove unneeded context
    - Parse curly brackets.
    """
    
    llm_readable_profile = profile.model_dump()
    
    # Remove score from posts and comments
    for post in llm_readable_profile["posts"]:
        post.pop("score", None)
    for comment in llm_readable_profile["comments"]:
        comment.pop("score", None)
        
    # Remove parent_submission from comments
    for comment in llm_readable_profile["comments"]:
        comment.pop("parent_submission", None)
        
    # Remove is_mod and is_gold
    llm_readable_profile.pop("is_mod", None)
    llm_readable_profile.pop("is_gold", None)
    llm_readable_profile.pop("link_karma", None)
    
    # Remove URLs
    for post in llm_readable_profile["posts"]:
        post.pop("url", None)
    for comment in llm_readable_profile["comments"]:
        comment.pop("url", None)
        
    # Turn into double curly brackets
    # like '{{"username":"xyz"}}'
    llm_readable_profile_str = json.dumps(llm_readable_profile)
    llm_readable_profile_str = llm_readable_profile_str.replace("{", "{{").replace("}", "}}")
    
    return llm_readable_profile_str
    
def make_profile_human_readable(profile: RedditUserProfile) -> str:
    output = [
        f"=== u/{profile.username} ===",
        f"Account created: {format_timestamp(profile.created_utc)}",
        f"Karma: {profile.total_karma} (Posts: {profile.link_karma}, Comments: {profile.comment_karma})",
        f"Moderator: {'Yes' if profile.is_mod else 'No'}",
        f"Reddit Premium: {'Yes' if profile.is_gold else 'No'}",
        "\n=== Posts ===",
    ]
    
    for post in profile.posts:
        output.extend([
            f"\nTitle: {post['title']}",
            f"Posted in r/{post['subreddit']} on {format_timestamp(post['created_utc'])}",
            f"Score: {post['score']}",
            f"URL: {post['url']}"
        ])
    
    output.append("\n=== Comments ===")
    
    for comment in profile.comments:
        output.extend([
            f"\nIn r/{comment['subreddit']} on {format_timestamp(comment['created_utc'])}",
            f"Score: {comment['score']}",
            f"Comment: {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}"
        ])
    
    return "\n".join(output)

def get_reddit_profile(username: str) -> RedditUserProfile | None:
    """
    Retrieves a Reddit user's profile from a file or scrapes it from Reddit if not found.
    """

    # Atempt to load from file in .profiles/
    filename = f"./.profiles/{username}/profile_data.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return RedditUserProfile.model_validate_json(f.read())
        except ValueError as e:
            print(f"Error loading JSON from {filename}: {e}")
            os.remove(filename)
    
    reddit = get_reddit_instance()
    user: Redditor = reddit.redditor(username)

    if user is None or hasattr(user, "error"):
        return None
    
    if user.is_suspended:
        return None
    
    print(f"Scraping profile for u/{username}")
    
    profile: RedditUserProfile = RedditUserProfile(
        username=user.name,
        comment_karma=user.comment_karma,
        link_karma=user.link_karma,
        total_karma=user.total_karma,
        created_utc=user.created_utc,
        is_mod=user.is_mod,
        is_gold=user.is_gold,
        posts=[],
        comments=[]
    )
    
    # Get all posts
    profile.posts = []
    for submission in user.submissions.new(limit=50):
        profile.posts.append({
            "title": submission.title,
            "selftext": submission.selftext,
            "score": submission.score,
            "url": submission.url,
            "created_utc": submission.created_utc,
            "subreddit": submission.subreddit.display_name
        })
    
    # Get all comments
    profile.comments = []
    for comment in user.comments.new(limit=50):
        submission = comment.submission
        profile.comments.append({
            "body": comment.body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "subreddit": comment.subreddit.display_name,
            "parent_submission": {
                "title": submission.title,
                "selftext": submission.selftext,
                "url": submission.url
            }
        })

    os.makedirs(f"./.profiles/{profile.username}", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(profile.model_dump_json())
        
    print(f"Profile saved to {filename}")

    return profile

if __name__ == "__main__":
    profile = get_reddit_profile("PastelGripPump")
    print(profile)


