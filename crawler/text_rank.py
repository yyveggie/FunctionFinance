import jieba
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from stopwords import stopwords, filter_stopwords
from langdetect import detect

class TextRanker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tokenizer = jieba.lcut
        self.zh_stop_words = self._load_stop_words('zh-cn')
        self.en_stop_words = self._load_stop_words('en')

    def _load_stop_words(self, language):
        if language == 'zh-cn':
            return stopwords('all')
        else:
            return stopwords('en')

    def detect_language(self, text):
        try:
            lang = detect(text)
            return lang
        except:
            return 'unknown'

    def rank_texts(self, texts):
        language = self.detect_language(texts[0])
        if language == 'zh-cn':
            texts = [' '.join(self.tokenizer(text)) for text in texts]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        words = self.vectorizer.get_feature_names_out()
        key_words_list = self._extract_keywords(texts, words, tfidf_matrix, language)
        similarity_matrix = self._calculate_similarity_matrix(texts, key_words_list, tfidf_matrix, words)
        scores = self._pagerank(similarity_matrix)
        return scores

    def _extract_keywords(self, texts, words, tfidf_matrix, language):
        key_words_list = []
        for i in range(len(texts)):
            doc_tfidf = tfidf_matrix[i].toarray()[0]
            if language == 'zh-cn':
                doc_words = [word for word in self.tokenizer(texts[i]) if word not in self.zh_stop_words]
            else:
                doc_words = [word for word in texts[i].split() if word not in self.en_stop_words]
            key_words = self._keywords(doc_words, words, doc_tfidf, texts, 10)
            key_words_list.append(key_words)
        return key_words_list

    def _keywords(self, document, words, tfidf_scores, documents, n):
        scores = [(word, tfidf * self._entropy(documents, word)) for word, tfidf in zip(words, tfidf_scores) if tfidf > 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [word for word, score in scores[:n]]

    def _entropy(self, documents, word):
        if documents[0].startswith('的'):  # 如果是中文文本
            freq = [[word for word in self.tokenizer(doc) if word not in self.zh_stop_words].count(word) for doc in documents]
        else:  # 如果是英文文本
            freq = [[word for word in doc.split() if word not in self.en_stop_words].count(word) for doc in documents]
        total = sum(freq)
        if total == 0:
            return 0
        probs = [f / total for f in freq]
        return -sum(p * math.log(p) for p in probs if p > 0)

    def _calculate_similarity_matrix(self, texts, key_words_list, tfidf_matrix, words):
        similarity_matrix = np.zeros((len(texts), len(texts)))
        for i in range(len(texts)):
            for j in range(len(texts)):
                doc_i_tfidf = [tfidf_matrix[i, np.where(words == word)[0][0]] if len(np.where(words == word)[0]) > 0 else 0 for word in key_words_list[i]]
                doc_j_tfidf = [tfidf_matrix[j, np.where(words == word)[0][0]] if len(np.where(words == word)[0]) > 0 else 0 for word in key_words_list[j]]
                similarity_matrix[i][j] = self._similarity(key_words_list[i], key_words_list[j], doc_i_tfidf, doc_j_tfidf)
        return similarity_matrix

    def _similarity(self, doc1, doc2, doc1_tfidf, doc2_tfidf):
        set1 = set(doc1)
        set2 = set(doc2)
        sum_min = 0
        sum_max = 0
        for word in set1 & set2:
            index1 = doc1.index(word)
            index2 = doc2.index(word)
            sum_min += min(doc1_tfidf[index1], doc2_tfidf[index2])
            sum_max += max(doc1_tfidf[index1], doc2_tfidf[index2])
        for word in set1 - set2:
            index1 = doc1.index(word)
            sum_max += doc1_tfidf[index1]
        for word in set2 - set1:
            index2 = doc2.index(word)
            sum_max += doc2_tfidf[index2]
        return sum_min / (sum_max + 1e-10)

    def _pagerank(self, A, max_iter=100, eps=0.0001, d=0.85):
        P = np.ones(len(A)) / len(A)
        for _ in range(max_iter):
            new_P = np.ones(len(A)) * (1 - d) / len(A)
            for i in range(len(A)):
                inlinks = np.where(A[:, i] != 0)[0]
                if len(inlinks) > 0:
                    new_P[i] += d * np.sum(P[inlinks] / np.sum(A[inlinks, :], axis=1))
            new_P /= np.sum(new_P)
            delta = np.abs(new_P - P).max()
            if delta <= eps:
                return new_P
            P = new_P
        return P

if __name__ == '__main__':
    # 示例用法
    # 示例文本数据
    news_texts = [
        "Python is an interpreted, high-level, general-purpose programming language. Created by Guido van Rossum and first released in 1991, Python's design philosophy emphasizes code readability with its notable use of significant whitespace.",
        "Machine learning (ML) is the scientific study of algorithms and statistical models that computer systems use to perform a specific task without using explicit instructions, relying on patterns and inference instead. It is seen as a subset of artificial intelligence.",
        "Quantum computing is the use of quantum-mechanical phenomena such as superposition and entanglement to perform computation. A quantum computer is used to perform such computation, which can be implemented theoretically or physically.",
        "The 2020 United States presidential election was the 59th quadrennial presidential election, held on Tuesday, November 3, 2020. The Democratic ticket of former vice president Joe Biden and the junior U.S. senator from California Kamala Harris defeated the incumbent Republican president Donald Trump and incumbent vice president Mike Pence.",
        "Climate change includes both the global warming driven by human emissions of greenhouse gases, and the resulting large-scale shifts in weather patterns. Though there have been previous periods of climatic change, since the mid-20th century, humans have had unprecedented impact on Earth's climate system and caused change on a global scale.",
        "The COVID-19 pandemic, also known as the coronavirus pandemic, is an ongoing global pandemic of coronavirus disease 2019 (COVID-19) caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2). The virus was first identified in December 2019 in Wuhan, China.",
        "Artificial intelligence (AI) is intelligence demonstrated by machines, unlike the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of 'intelligent agents': any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.",
        "你好,这是一段中文文本。自然语言处理是人工智能领域的一个重要分支,它研究如何让计算机理解和生成人类语言。近年来,深度学习技术的发展极大地推动了自然语言处理的进步。"
    ]
    text_ranker = TextRanker()
    scores = text_ranker.rank_texts(news_texts)

    # 打印每个文本的分数
    for score in scores:
        print(f"{score:.3f}")