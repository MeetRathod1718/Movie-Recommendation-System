This Movie Recommendation System is built using a variety of technologies to ensure optimal performance and a seamless user experience. 
The core of the application is written in Python, utilizing libraries such as Streamlit for the interactive web interface, scikit-learn for implementing machine learning algorithms, and Pandas and NumPy for efficient data manipulation and analysis. 
The system fetches movie data using IMDbPY and web scraping techniques with BeautifulSoup to gather additional information about movies. The recommendation engine uses unsupervised learning techniques, specifically content-based filtering, where the system suggests movies based on the similarity of content (such as genre, director, cast, etc.) to those the user has previously interacted with.
By analyzing the features of movies and user preferences, the system is able to provide personalized and accurate movie recommendations without relying on labeled data.

## Installation Steps

Follow the instructions below to set up the **Movie Recommendation System** on your local machine.

### Prerequisites

Make sure you have **Python 3.6+** and **pip** installed. If not, please download and install Python from [python.org](https://www.python.org/downloads/).

### 1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/MeetRathod1718/Movie-Recommendation-System


2. Navigate to the Project Directory

cd movie-recommendation-system

3. Set Up a Virtual Environment (Optional but Recommended)

python -m venv venv


Activate the virtual environment:

Windows:

venv\Scripts\activate

For MacOS:

source venv/bin/activate

4. Install the Required Dependencies

pip install -r requirements.txt

5. Run the Application

streamlit run app1.py
