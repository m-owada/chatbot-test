# coding: UTF-8
import MeCab
import json
import re
from random import choice
from gensim.models import word2vec

class Chatbot:
    def __init__(self, name, dictionary, sentences):
        self._name = name
        if dictionary:
            self._dictionary = json.loads(dictionary)
        else:
            self._dictionary = {}
        if sentences:
            self._sentences = json.loads(sentences)
        else:
            self._sentences = []

    # メッセージ返信
    def response(self, message, debug=False):
        part = self.analysis(message)
        model = self.get_model()
        p, res, log = "", "", ""
        while part and not res:
            p = choice(part)
            for item in self.similar(model, p):
                res = self.chain(item[0])
                log = "Word2Vec : " + p + " > " + item[0] + " (" + str(item[1]) + ")"
                if res:
                    break
            part.remove(p)
        if not res:
            res = self.template(message)
        if debug:
            res = res + " " + log
        return res

    # メッセージ解析
    def analysis(self, message):
        tagger = MeCab.Tagger("-Ochasen")
        tagger.parse("")
        node = tagger.parseToNode(message)
        key1, key2 = "", ""
        part = []
        while node:
            if node.surface.strip():
                self.add_dictionary(key1, key2, node.surface)
                key1, key2 = key2, node.surface
                if self.chk_keyword(node.feature):
                    part.append(node.surface)
            node = node.next
        self.add_dictionary(key1, key2, "")
        self.add_sentences(part)
        return part

    # 単語追加
    def add_dictionary(self, key1, key2, word):
        if key1 and key2:
            if not key1 in self._dictionary:
                self._dictionary[key1] = {}
            if not key2 in self._dictionary[key1]:
                self._dictionary[key1][key2] = []
            self._dictionary[key1][key2].append(word)
        return

    # キーワード確認
    def chk_keyword(self, word):
        if re.match(r"連体詞|接頭詞|名詞|動詞,自立|形容詞,自立|副詞|接続詞|感動詞|未知語", word):
            if not re.match(r"名詞,接尾|名詞,非自立", word):
                return True
        return False

    # キーワード追加
    def add_sentences(self, part):
        self._sentences.append(part)

    # Word2Vecモデル生成
    def get_model(self):
        return word2vec.Word2Vec(self._sentences, size=100, min_count=1, window=3, iter=100)

    # Word2Vec単語抽出
    def similar(self, model, word):
        if word in model.wv:
            return model.wv.most_similar(positive=[word])
        else:
            return [[word, 0]]

    # メッセージ生成
    def chain(self, key1):
        count = 0
        key2, tmp = "", ""
        if key1 in self._dictionary:
            key2 = choice(list(self._dictionary[key1].keys()))
        message = key1 + key2
        while count < 100:
            if self.chk_dictionary(key1, key2):
                tmp = choice(self._dictionary[key1][key2])
                message += tmp
                key1, key2 = key2, tmp
                if re.match(r"[。?？!！]", tmp):
                    break
            else:
                break
            count += 1
        if count == 0:
            message = ""
        elif count == 100:
            message += "..."
        return message

    # 単語確認
    def chk_dictionary(self, key1, key2):
        if key1 and key2:
            if key1 in self._dictionary:
                if key2 in self._dictionary[key1]:
                    if self._dictionary[key1][key2]:
                        return True
        return False

    # 定型文
    def template(self, message):
        if re.search(r"[?？]", message):
            return "よくわかりません。"
        else:
            return "そうですね。"

    @property
    def name(self):
        return self._name

    @property
    def dictionary(self):
        return self._dictionary

    @property
    def sentences(self):
        return self._sentences

    @property
    def json_dictionary(self):
        return json.dumps(self._dictionary, ensure_ascii=False)

    @property
    def json_sentences(self):
        return json.dumps(self._sentences, ensure_ascii=False)
