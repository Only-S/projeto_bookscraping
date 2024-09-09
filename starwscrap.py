import requests
from bs4 import BeautifulSoup
import csv
import re
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

# Requisição do HTML
url = 'https://www.goodreads.com/book/show/203690153-ordem-paranormal-vol-2'
response = requests.get(url)

# Seleção dos elementos do DOM
soup = BeautifulSoup(response.content, 'html.parser')
reviews = soup.find_all('article', class_='ReviewCard')

# Carregar dataset em memória
comments_list = []
for review in reviews:
    username = review.find('div', class_='ReviewerProfile__name').get_text().strip()
    review_date = review.find('span', class_='Text Text__body3').get_text().strip()
    likes = review.find('div', class_='SocialFooter__statsContainer').get_text().strip() if review.find('div', class_='SocialFooter__statsContainer') else ''
    review_content = review.find('span', class_='Formatted')
    content_text = review_content.get_text(separator=" ").strip()
    
    comments_list.append({
        'Autor': username,        
        'Data': review_date,
        'Likes': likes,
        'Texto da Review': content_text
    })

# Salvar o dataset em CSV
with open('goodreads_reviews.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Autor', 'Data', 'Likes', 'Texto da Review'])
    writer.writeheader()
    writer.writerows(comments_list)

print("Comentários extraídos e salvos em 'goodreads_reviews.csv'")

# Carregar o dataset do CSV
data = pd.read_csv('goodreads_reviews.csv')
comments = data['Texto da Review'].tolist()

# Definição das stopwords
nltk.download('stopwords')
stop_wordsPT = set(stopwords.words('portuguese'))
stop_wordsEN = set(stopwords.words('english'))

# Lista customizada de stopwords
custom_stopwords = {'cena', 'pra', 'tá'}

# Incluir stopwords personalizadas às stopwrods padrões
stop_words = stop_wordsPT.union(stop_wordsEN).union(custom_stopwords)

# Pré-processamento do texto
def preprocess_text(text):
    text = text.lower()  # Converte para minúsculas
    text = re.sub(r'\d+', '', text)  # Remove números
    text = re.sub(r'[^\w\s]', '', text)  # Remove pontuação
    words = text.split()
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    return ' '.join(words)

# Aplicar o pré-processamento em cada comentário
cleaned_comments = [preprocess_text(comment) for comment in comments]

# Unir todos os comentários em um único texto
all_comments = ' '.join(cleaned_comments)

# Gerar a nuvem de palavras
wordcloud = WordCloud(width=1080, height=720, background_color='white').generate(all_comments)

# Exibir e salvar a nuvem de palavras
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('wordcloud.png')