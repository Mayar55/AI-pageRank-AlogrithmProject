import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import re
import random

DAMPING = 0.85
SAMPLES = 10000

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_probabilities = {}
    linked_pages = corpus[page] if page in corpus else corpus.keys()

    # Probability of choosing a link from the current page
    link_prob = damping_factor / len(linked_pages) if linked_pages else 0

    # Probability of choosing a random page from the corpus
    random_prob = (1 - damping_factor) / len(corpus)

    # Assign probabilities
    for p in corpus:
        transition_probabilities[p] = random_prob
    for p in linked_pages:
        transition_probabilities[p] += link_prob

    return transition_probabilities

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {page: 0 for page in corpus}

    # Start with a random page
    current_page = random.choice(list(corpus.keys()))

    for _ in range(n):
        # Update the page rank of the current page
        page_rank[current_page] += 1 / n

        # Transition to the next page based on transition model
        transition_probabilities = transition_model(corpus, current_page, damping_factor)
        next_page = random.choices(list(transition_probabilities.keys()), weights=transition_probabilities.values())[0]

        # Move to the next page
        current_page = next_page

    return page_rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    page_rank = {page: 1 / N for page in corpus}

    # Calculate page rank iteratively until convergence
    while True:
        new_page_rank = {}

        # Calculate new page ranks for each page
        for page in corpus:
            total = (1 - damping_factor) / N

            # Sum up the contribution of each page linking to the current page
            for linking_page, linked_pages in corpus.items():
                if page in linked_pages:
                    total += damping_factor * page_rank[linking_page] / len(linked_pages)

            new_page_rank[page] = total

        # Check for convergence
        if all(abs(new_page_rank[page] - page_rank[page]) < 0.001 for page in corpus):
            break

        # Update page ranks for the next iteration
        page_rank = new_page_rank

    return page_rank

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Call your existing code with the selected folder path
        corpus = crawl(folder_path)
        
        # Perform PageRank analysis using both approaches
        ranks_sampling = sample_pagerank(corpus, DAMPING, SAMPLES)
        ranks_iteration = iterate_pagerank(corpus, DAMPING)
        
        # Display the results
        display_results(ranks_sampling, ranks_iteration)

def display_results(ranks_sampling, ranks_iteration):
    # Clear previous results
    result_text.delete(1.0, tk.END)
    
    # Display results for sampling approach
    result_text.insert(tk.END, "PageRank Results from Sampling\n")
    for page, rank in sorted(ranks_sampling.items()):
        result_text.insert(tk.END, f"{page}: {rank:.4f}\n")
    result_text.insert(tk.END, "\n")
    
    # Display results for iteration approach
    result_text.insert(tk.END, "PageRank Results from Iteration\n")
    for page, rank in sorted(ranks_iteration.items()):
        result_text.insert(tk.END, f"{page}: {rank:.4f}\n")

# Create the main application window
root = tk.Tk()
root.title("PageRank Analyzer")

# Create a frame for the folder selection button
frame_select = tk.Frame(root)
frame_select.pack(pady=10)

# Create a button for folder selection
select_button = tk.Button(frame_select, text="Select Folder", command=select_folder)
select_button.pack(side=tk.LEFT, padx=5)

# Create a text area to display results
result_text = tk.Text(root, height=20, width=50)
result_text.pack(padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
