import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import praw
import time
import logging
import random
import os
from dotenv import load_dotenv
from PIL import Image, ImageTk

# Load environment variables from .env file
load_dotenv()

class RedditPosterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Reddit Post Automater")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize Reddit client
        self.reddit = None
        self.init_reddit_client()
        
        # Variables
        self.image_path = tk.StringVar()
        self.post_title = tk.StringVar()
        self.comment_text = tk.StringVar(value="yo this is the sauce")
        self.subreddits_text = tk.StringVar(value="test")
        
        # Create GUI elements
        self.create_widgets()
        
        # Configure logging to show in GUI
        self.setup_logging()
    
    def init_reddit_client(self):
        """Initialize Reddit client with credentials from .env"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                password=os.getenv('REDDIT_PASSWORD'),
                user_agent=os.getenv('REDDIT_USER_AGENT'),
                username=os.getenv('REDDIT_USERNAME'),
            )
            # Test authentication
            user = self.reddit.user.me()
            self.auth_status = f"✅ Authenticated as: {user}"
        except Exception as e:
            self.auth_status = f"❌ Authentication failed: {str(e)}"
            self.reddit = None
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Reddit Post Automater", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Authentication status
        auth_label = ttk.Label(main_frame, text=self.auth_status, 
                              font=("Arial", 10))
        auth_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Post Title
        ttk.Label(main_frame, text="Post Title:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        title_entry = ttk.Entry(main_frame, textvariable=self.post_title, width=50)
        title_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Image Selection
        ttk.Label(main_frame, text="Select Image:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        image_frame.columnconfigure(0, weight=1)
        
        self.image_label = ttk.Label(image_frame, text="No image selected")
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(image_frame, text="Browse Image", 
                  command=self.browse_image).grid(row=0, column=1, padx=(10, 0))
        
        # Image preview
        self.image_preview = ttk.Label(main_frame, text="")
        self.image_preview.grid(row=6, column=0, columnspan=2, pady=(0, 15))
        
        # Subreddits
        ttk.Label(main_frame, text="Subreddits (comma-separated):", 
                 font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        subreddits_entry = ttk.Entry(main_frame, textvariable=self.subreddits_text, width=50)
        subreddits_entry.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Comment Text
        ttk.Label(main_frame, text="Comment Text:", font=("Arial", 10, "bold")).grid(
            row=9, column=0, sticky=tk.W, pady=(0, 5))
        comment_entry = ttk.Entry(main_frame, textvariable=self.comment_text, width=50)
        comment_entry.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Post Button
        self.post_button = ttk.Button(main_frame, text="🚀 Post to Reddit", 
                                     command=self.start_posting, style="Accent.TButton")
        self.post_button.grid(row=11, column=0, columnspan=2, pady=(0, 20))
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Log Display
        ttk.Label(main_frame, text="Activity Log:", font=("Arial", 10, "bold")).grid(
            row=13, column=0, sticky=tk.W, pady=(0, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70)
        self.log_text.grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configure row weight for log text to expand
        main_frame.rowconfigure(14, weight=1)
        
        # Clear Log Button
        ttk.Button(main_frame, text="Clear Log", 
                  command=self.clear_log).grid(row=15, column=0, columnspan=2)
    
    def setup_logging(self):
        """Setup logging to display in GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                # Schedule the GUI update in the main thread
                self.text_widget.after(0, append)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Add GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(gui_handler)
        self.logger.setLevel(logging.INFO)
    
    def browse_image(self):
        """Open file dialog to select image"""
        filetypes = (
            ('Image files', '*.jpg *.jpeg *.png *.gif *.webp'),
            ('JPEG files', '*.jpg *.jpeg'),
            ('PNG files', '*.png'),
            ('GIF files', '*.gif'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select an image',
            initialdir=os.path.expanduser('~'),
            filetypes=filetypes
        )
        
        if filename:
            self.image_path.set(filename)
            self.image_label.config(text=os.path.basename(filename))
            self.show_image_preview(filename)
    
    def show_image_preview(self, image_path):
        """Show a preview of the selected image"""
        try:
            # Open and resize image for preview
            with Image.open(image_path) as img:
                # Calculate size to fit in preview area (max 200x200)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Update preview label
                self.image_preview.config(image=photo)
                self.image_preview.image = photo  # Keep a reference
                
        except Exception as e:
            self.image_preview.config(image='', text=f"Preview error: {str(e)}")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.post_title.get().strip():
            messagebox.showerror("Error", "Please enter a post title")
            return False
        
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image")
            return False
        
        if not os.path.exists(self.image_path.get()):
            messagebox.showerror("Error", "Selected image file does not exist")
            return False
        
        if not self.subreddits_text.get().strip():
            messagebox.showerror("Error", "Please enter at least one subreddit")
            return False
        
        if not self.reddit:
            messagebox.showerror("Error", "Reddit authentication failed. Check your .env file")
            return False
        
        return True
    
    def start_posting(self):
        """Start the posting process in a separate thread"""
        if not self.validate_inputs():
            return
        
        # Disable the post button and start progress bar
        self.post_button.config(state='disabled')
        self.progress.start()
        
        # Start posting in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self.post_to_reddit)
        thread.daemon = True
        thread.start()
    
    def post_to_reddit(self):
        """Post to Reddit (runs in separate thread)"""
        try:
            # Parse subreddits
            subreddit_list = [s.strip() for s in self.subreddits_text.get().split(',') if s.strip()]
            
            self.logger.info(f"Starting to post to {len(subreddit_list)} subreddits...")
            
            # Post to subreddits
            successful, failed, submissions = self.post_to_subreddits(
                title=self.post_title.get(),
                subreddit_list=subreddit_list,
                image_path=self.image_path.get()
            )
            
            # Comment on successful posts
            if submissions and self.comment_text.get().strip():
                self.logger.info(f"Starting to comment on {len(submissions)} successful posts...")
                self.comment_on_posts(submissions, self.comment_text.get())
            
            # Show completion message
            total_posts = len(subreddit_list)
            success_count = len(successful)
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Posting Complete", 
                f"Posted to {success_count}/{total_posts} subreddits successfully!"
            ))
            
        except Exception as e:
            self.logger.error(f"Error during posting: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Posting failed: {str(e)}"))
        
        finally:
            # Re-enable button and stop progress bar
            self.root.after(0, lambda: [
                self.post_button.config(state='normal'),
                self.progress.stop()
            ])
    
    def post_to_subreddits(self, title, subreddit_list, image_path):
        """Post to multiple subreddits (adapted from original function)"""
        successful_posts = []
        failed_posts = []
        submissions = []
        
        for subreddit_name in subreddit_list:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                submission = subreddit.submit_image(title=title, image_path=image_path, nsfw=False)
                
                self.logger.info(f"✅ Successfully posted to r/{subreddit_name}: {submission.url}")
                successful_posts.append(subreddit_name)
                submissions.append(submission)
                
                # Add delay between posts
                if subreddit_name != subreddit_list[-1]:
                    delay = random.randint(20, 40)
                    self.logger.info(f"⏳ Waiting {delay} seconds before next post...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to post to r/{subreddit_name}: {str(e)}")
                failed_posts.append(subreddit_name)
        
        return successful_posts, failed_posts, submissions
    
    def comment_on_posts(self, submissions, comment_text):
        """Comment on successful posts (adapted from original function)"""
        successful_comments = []
        failed_comments = []
        
        for submission in submissions:
            try:
                comment = submission.reply(comment_text)
                self.logger.info(f"💬 Successfully commented on r/{submission.subreddit.display_name}")
                successful_comments.append(submission.subreddit.display_name)
                
                # Add delay between comments
                if submission != submissions[-1]:
                    delay = random.randint(15, 30)
                    self.logger.info(f"⏳ Waiting {delay} seconds before next comment...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"❌ Failed to comment on r/{submission.subreddit.display_name}: {str(e)}")
                failed_comments.append(submission.subreddit.display_name)
        
        return successful_comments, failed_comments

def main():
    root = tk.Tk()
    app = RedditPosterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
