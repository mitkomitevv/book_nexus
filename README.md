# Book Nexus

**Book Nexus** is a Django-powered platform designed for book enthusiasts to explore, review, and organize their reading experiences. The project focuses on delivering a clean and functional backend while supporting essential features for managing books, reviews, ratings, and user interactions.

---

## Features

- **Book Management:** Add, view, and manage books with their details, including author relationships and series.
- **Ratings and Reviews:** Users can rate books and leave detailed reviews. Ratings are handled via a dedicated model for flexibility.
- **Reading List:** Easily add books to personalized reading lists, with status updates showing whether a book is currently in a list.
- **Search Functionality:** Search for books by title or author, with contextual reading list integration.
- **Follow System:** A simple follow feature lets users keep up with reviews from others they follow.
- **Comments:** Add comments to reviews for discussion and engagement.
- **Staff Permissions:** Certain actions, like adding books, authors, or series, are restricted to staff users.

---

## Live Demo

Try out the live version of **Book Nexus**:  
[Book Nexus Live](https://book-nexus-aygfb9hffqdadzge.germanywestcentral-01.azurewebsites.net/)

---

## Local Installation

Follow these steps to set up **Book Nexus** locally:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/mitkomitevv/book_nexus.git
    ```

2. **Set up a virtual environment and install dependencies:**
    ```bash
    python -m venv .env
    source env/bin/activate  # On Windows: .env\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

4. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

---

## Usage

- Explore books and see reviews from users you follow.
- Add books to your reading list and manage their status.
- Rate and review books, or engage with others' reviews through comments.
- Search for books and view their details, including relationships with authors and series.

---

## Future Plans

- **Frontend Enhancements:** While currently backend-focused, the project can be expanded with a robust frontend in the future.
- **Advanced Features:** Potential features like recommendation systems, advanced filtering, and book clubs could be added post-project.
