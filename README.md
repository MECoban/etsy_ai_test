# Etsy AI Listing Assistant

An AI-powered tool to help Etsy sellers create optimized listings with keywords, titles, and product images using OpenAI's APIs.

## Features

- **AI Keyword Generation**: Generate SEO-optimized keywords for your Etsy listings
- **AI Title Generation**: Create compelling, search-friendly titles for your products
- **AI Image Generation**: Create professional product images with DALL-E
- **Image Enhancement**: Enhance your existing product images (remove backgrounds, improve quality)

## Technologies Used

- Python 3.x
- Flask (Web Framework)
- OpenAI API (GPT-4, DALL-E)
- Bootstrap 5 (Frontend)

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/etsy-ai-assistant.git
cd etsy-ai-assistant
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key
```bash
cp .env.example .env
# Edit .env file and add your OpenAI API key
```

## Running the Application

1. Start the Flask server
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter your product description and category
2. Generate SEO-optimized keywords
3. Select keywords and generate compelling titles
4. Create professional product images or enhance existing ones
5. Use the generated content for your Etsy listings

## License

This project is licensed under the MIT License - see the LICENSE file for details. 