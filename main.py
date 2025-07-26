import praw
import time
import logging
from praw.models import InlineImage
import random
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    password=os.getenv('REDDIT_PASSWORD'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
    username=os.getenv('REDDIT_USERNAME'),
)

def post_to_subreddits(title, content, subreddit_list, post_type="text", url=None, image_path=None, delay=60):
    """
    Post to multiple subreddits with a delay between posts
    
    Args:
        title (str): The title of the post
        content (str): The content/selftext of the post (for text posts)
        subreddit_list (list): List of subreddit names to post to
        post_type (str): "text" for text posts, "link" for link posts, "image" for image posts
        url (str): URL for link posts (required if post_type="link")
        image_path (str): Path to image file (required if post_type="image")
        delay (int): Delay in seconds between posts (default: 60)
    
    Returns:
        tuple: (successful_posts, failed_posts, submissions) where submissions is a list of submission objects
    """
    
    successful_posts = []
    failed_posts = []
    submissions = []  # Store submission objects for commenting later
    
    for subreddit_name in subreddit_list:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            
            if post_type == "text":
                submission = subreddit.submit(title=title, selftext=content)
            elif post_type == "link":
                if not url:
                    logger.error(f"URL required for link post to r/{subreddit_name}")
                    failed_posts.append(subreddit_name)
                    continue
                submission = subreddit.submit(title=title, url=url)
            elif post_type == "image":
                if not image_path:
                    logger.error(f"Image path required for image post to r/{subreddit_name}")
                    failed_posts.append(subreddit_name)
                    continue
                # Check if image file exists
                import os
                if not os.path.exists(image_path):
                    logger.error(f"Image file not found: {image_path}")
                    failed_posts.append(subreddit_name)
                    continue
                submission = subreddit.submit_image(title=title, image_path=image_path, nsfw=False)
            else:
                logger.error(f"Invalid post type: {post_type}")
                failed_posts.append(subreddit_name)
                continue
            
            logger.info(f"Successfully posted to r/{subreddit_name}: {submission.url}")
            successful_posts.append(subreddit_name)
            submissions.append(submission)  # Store submission for later commenting
            
            # Add delay between posts to avoid rate limiting
            if subreddit_name != subreddit_list[-1]:  # Don't delay after last post
                logger.info(f"Waiting {delay} seconds before next post...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Failed to post to r/{subreddit_name}: {str(e)}")
            failed_posts.append(subreddit_name)
    
    # Summary
    logger.info(f"\nPosting complete!")
    logger.info(f"Successful posts: {len(successful_posts)}")
    logger.info(f"Failed posts: {len(failed_posts)}")
    
    if successful_posts:
        logger.info(f"Posted successfully to: {', '.join(successful_posts)}")
    if failed_posts:
        logger.info(f"Failed to post to: {', '.join(failed_posts)}")
    
    return successful_posts, failed_posts, submissions

def comment_on_posts(submissions, comment_text, delay=30):
    """
    Comment on a list of submissions
    
    Args:
        submissions (list): List of submission objects to comment on
        comment_text (str): The comment text to post
        delay (int): Delay in seconds between comments (default: 30)
    
    Returns:
        tuple: (successful_comments, failed_comments)
    """
    successful_comments = []
    failed_comments = []
    
    logger.info(f"\nStarting to comment on {len(submissions)} posts...")
    
    for submission in submissions:
        try:
            # Add comment to the submission
            comment = submission.reply(comment_text)
            logger.info(f"Successfully commented on post in r/{submission.subreddit.display_name}: {comment.permalink}")
            successful_comments.append(submission.subreddit.display_name)
            
            # Add delay between comments to avoid rate limiting
            if submission != submissions[-1]:  # Don't delay after last comment
                logger.info(f"Waiting {delay} seconds before next comment...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Failed to comment on post in r/{submission.subreddit.display_name}: {str(e)}")
            failed_comments.append(submission.subreddit.display_name)
    
    # Summary
    logger.info(f"\nCommenting complete!")
    logger.info(f"Successful comments: {len(successful_comments)}")
    logger.info(f"Failed comments: {len(failed_comments)}")
    
    if successful_comments:
        logger.info(f"Commented successfully on: {', '.join(successful_comments)}")
    if failed_comments:
        logger.info(f"Failed to comment on: {', '.join(failed_comments)}")
    
    return successful_comments, failed_comments

# Example usage
if __name__ == "__main__":
    # Check if we can authenticate
    try:
        logger.info(f"Authenticated as: {reddit.user.me()}")
        logger.info(f"Read-only mode: {reddit.read_only}")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        exit(1)
    
    # Example configuration - modify these values
    POST_TITLE = "you say perfection, i show this"
    POST_CONTENT = ""
    IMAGE_PATH = "/Users/aparimit/Downloads/postAutomater/testimage.jpg"  # Path to your image file
    COMMENT_TEXT = "yo this is the sauce"
    
    # List of subreddits to post to
    SUBREDDITS = ["test", "HentaiOnlyGoodHentai"]  # Replace with your subreddits

    # For text posts
    # print("Starting to post to subreddits...")
    # successful, failed = post_to_subreddits(
    #     title=POST_TITLE,
    #     content=POST_CONTENT,
    #     subreddit_list=SUBREDDITS,
    #     post_type="text",
    #     delay=60  # 60 seconds between posts
    # )
    
    # For image posts
    print("Starting to post image to subreddits...")
    successful, failed, submissions = post_to_subreddits(
        title=POST_TITLE,
        content="",  # Not used for image posts
        subreddit_list=SUBREDDITS,
        post_type="image",
        image_path=IMAGE_PATH,
        delay=random.randint(20, 40)  # Random delay between 20-40 seconds
    )
    
    # Comment on successful posts
    if submissions:
        print(f"\nFound {len(submissions)} successful posts. Starting to comment...")
        successful_comments, failed_comments = comment_on_posts(
            submissions=submissions,
            comment_text=COMMENT_TEXT,
            delay=random.randint(15, 30)  # Random delay between 15-30 seconds
        )
    else:
        print("No successful posts to comment on.")
    
    # Example for link posts (uncomment to use)
    # successful, failed = post_to_subreddits(
    #     title="Check out this cool website",
    #     content="",  # Not used for link posts
    #     subreddit_list=SUBREDDITS,
    #     post_type="link",
    #     url="https://www.example.com",
    #     delay=60
    # )