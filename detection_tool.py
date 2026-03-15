import os
import sys
import json
import time
import hashlib
import pickle
import sqlite3
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import PyPDF2
import docx
from bs4 import BeautifulSoup
import requests
import warnings
warnings.filterwarnings('ignore')

class TextProcessor:
    def __init__(self):
        self.stopwords = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                              'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                              'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                              'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                              'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                              'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                              'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
                              'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                              'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                              'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                              'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                              'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
        
    def clean_text(self, text):
        text = text.lower()
        words = text.split()
        words = [word for word in words if word.isalnum() and word not in self.stopwords and len(word) > 2]
        return ' '.join(words)
    
    def extract_from_file(self, filepath):
        path = Path(filepath)
        if not path.exists():
            return ''
            
        ext = path.suffix.lower()
        text = ''
        
        try:
            if ext == '.txt':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            elif ext == '.pdf':
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() or ''
            elif ext == '.docx':
                doc = docx.Document(filepath)
                text = '\n'.join([p.text for p in doc.paragraphs])
            elif ext in ['.html', '.htm']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    text = soup.get_text()
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
        except:
            return ''
            
        return self.clean_text(text)

class FingerprintGenerator:
    def __init__(self, window_size=5, hash_bits=64):
        self.window_size = window_size
        self.hash_bits = hash_bits
        
    def generate(self, text):
        words = text.split()
        if len(words) < self.window_size:
            return []
            
        fingerprints = []
        for i in range(len(words) - self.window_size + 1):
            window = ' '.join(words[i:i+self.window_size])
            hash_obj = hashlib.sha256(window.encode())
            hash_int = int(hash_obj.hexdigest(), 16) & ((1 << self.hash_bits) - 1)
            fingerprints.append(hash_int)
            
        min_hashes = []
        for i in range(0, len(fingerprints) - 4):
            min_hash = min(fingerprints[i:i+5])
            min_hashes.append(min_hash)
            
        return list(set(min_hashes))

class SimilarityEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 4),
            max_features=5000,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode',
            analyzer='word',
            token_pattern=r'\w+',
            norm='l2',
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True
        )
        
    def compute_matrix(self, documents):
        if len(documents) < 2:
            return np.array([[1.0]])
            
        tfidf = self.vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf)
        return similarity

class ClusterAnalyzer:
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        
    def analyze(self, similarity_matrix):
        distance = 1 - similarity_matrix
        np.fill_diagonal(distance, 0)
        
        kmeans = KMeans(n_clusters=min(5, len(distance)), random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(distance)
        
        condensed = pdist(distance)
        linkage_matrix = linkage(condensed, method='average')
        hierarchical_labels = fcluster(linkage_matrix, t=self.threshold, criterion='distance')
        
        return {
            'kmeans': kmeans_labels.tolist(),
            'hierarchical': hierarchical_labels.tolist(),
            'linkage': linkage_matrix.tolist()
        }

class ReportBuilder:
    def __init__(self):
        self.data = {}
        
    def build(self, filenames, similarity, clusters, fingerprints):
        pairs = []
        for i in range(len(filenames)):
            for j in range(i+1, len(filenames)):
                if similarity[i][j] > 0.5:
                    pairs.append({
                        'a': filenames[i],
                        'b': filenames[j],
                        'score': float(similarity[i][j])
                    })
                    
        stats = []
        for i, f in enumerate(filenames):
            others = np.delete(similarity[i], i)
            stats.append({
                'file': f,
                'max_sim': float(np.max(others)) if len(others) > 0 else 0,
                'avg_sim': float(np.mean(others)) if len(others) > 0 else 0,
                'cluster': int(clusters['hierarchical'][i]),
                'fingerprints': len(fingerprints[i]) if i < len(fingerprints) else 0
            })
            
        self.data = {
            'timestamp': time.time(),
            'files': filenames,
            'total': len(filenames),
            'similar_pairs': pairs,
            'statistics': stats,
            'matrix': similarity.tolist()
        }
        return self.data
    
    def save_json(self, path):
        with open(path, 'w') as f:
            json.dump(self.data, f, indent=2)

class Database:
    def __init__(self, db_path='plagiarism.db'):
        self.db_path = db_path
        self.init_db()
        
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                text TEXT,
                fingerprint TEXT,
                created_at REAL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc1_id INTEGER,
                doc2_id INTEGER,
                similarity REAL,
                compared_at REAL,
                FOREIGN KEY(doc1_id) REFERENCES documents(id),
                FOREIGN KEY(doc2_id) REFERENCES documents(id)
            )
        ''')
        conn.commit()
        conn.close()
        
    def save_document(self, filename, text, fingerprints):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute(
                'INSERT OR REPLACE INTO documents (filename, text, fingerprint, created_at) VALUES (?, ?, ?, ?)',
                (filename, text[:1000], json.dumps(fingerprints), time.time())
            )
            conn.commit()
        except:
            pass
        conn.close()

class WebChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def check(self, text, max_results=5):
        if len(text) < 100:
            return []
            
        query = text[:200].replace(' ', '+')
        url = f'https://www.google.com/search?q={query}'
        
        try:
            r = self.session.get(url, timeout=3)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            urls = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and 'url?q=' in href:
                    url = href.split('url?q=')[1].split('&')[0]
                    if 'http' in url:
                        urls.append(url)
                        
            results = []
            for url in urls[:max_results]:
                try:
                    r2 = self.session.get(url, timeout=3)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    content = soup2.get_text()[:1000]
                    
                    vec = TfidfVectorizer().fit_transform([text, content])
                    sim = cosine_similarity(vec[0:1], vec[1:2])[0][0]
                    
                    results.append({
                        'url': url,
                        'similarity': float(sim)
                    })
                except:
                    continue
                    
            return sorted(results, key=lambda x: x['similarity'], reverse=True)
        except:
            return []

class BatchProcessor:
    def __init__(self, workers=4):
        self.workers = workers
        
    def process(self, files, func):
        results = []
        total = len(files)
        
        for i, file in enumerate(files):
            try:
                result = func(file)
                results.append(result)
                print(f'Progress: {i+1}/{total}', end='\r')
            except:
                results.append(None)
                
        return results

def main():
    if len(sys.argv) < 2:
        print('Usage: python detector.py <file1> <file2> ...')
        print('       python detector.py <directory>')
        sys.exit(1)
        
    files = []
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_dir():
            files.extend([str(f) for f in path.glob('*.*') if f.suffix.lower() in ['.txt', '.pdf', '.docx']])
        else:
            files.append(arg)
            
    if len(files) < 2:
        print('Need at least 2 files')
        sys.exit(1)
        
    print(f'Processing {len(files)} files...')
    
    processor = TextProcessor()
    fingerprint_gen = FingerprintGenerator()
    engine = SimilarityEngine()
    cluster_analyzer = ClusterAnalyzer()
    reporter = ReportBuilder()
    db = Database()
    web = WebChecker()
    
    texts = []
    fingerprints = []
    valid_files = []
    
    for file in files:
        text = processor.extract_from_file(file)
        if text:
            texts.append(text)
            valid_files.append(file)
            fp = fingerprint_gen.generate(text)
            fingerprints.append(fp)
            db.save_document(file, text, fp)
            
    if len(texts) < 2:
        print('Not enough valid files')
        sys.exit(1)
        
    print('Computing similarity...')
    similarity = engine.compute_matrix(texts)
    
    print('Analyzing clusters...')
    clusters = cluster_analyzer.analyze(similarity)
    
    print('Building report...')
    report = reporter.build(valid_files, similarity, clusters, fingerprints)
    reporter.save_json('report.json')
    
    print('Checking online sources...')
    suspicious = []
    for i, text in enumerate(texts):
        if np.max(np.delete(similarity[i], i)) > 0.7:
            results = web.check(text)
            if results:
                suspicious.append({
                    'file': valid_files[i],
                    'matches': results[:2]
                })
                
    if suspicious:
        with open('suspicious.json', 'w') as f:
            json.dump(suspicious, f, indent=2)
            
    print('\nResults:')
    print(f'Files analyzed: {len(valid_files)}')
    print(f'Similar pairs found: {len(report["similar_pairs"])}')
    
    for pair in report['similar_pairs'][:5]:
        print(f'  {Path(pair["a"]).name} ~ {Path(pair["b"]).name}: {pair["score"]:.2%}')

if __name__ == '__main__':
    main()
