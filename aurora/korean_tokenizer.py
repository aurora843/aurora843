# 파일 이름: korean_tokenizer.py

from __future__ import annotations
from typing import Any, Dict, List, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message

# === Token 클래스 경로를 수정합니다 ===
# 이전 시도: from rasa.shared.nlu.training_data.tokens import Token
# 새로운 시도 (Rasa 2.x 후반 ~ 3.x 초반에 사용되던 경로):
from rasa.nlu.tokenizers.token import Token # <<< 경로 수정
from rasa.nlu.tokenizers.tokenizer import Tokenizer
# ====================================

from konlpy.tag import Okt

@DefaultV1Recipe.register(DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False)
class KoNLPyOktTokenizer(Tokenizer, GraphComponent):
    """Rasa 3.x 호환 KoNLPy Okt 토크나이저."""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> KoNLPyOktTokenizer:
        return cls(config)

    def __init__(self, config: Dict[Text, Any]) -> None:
        super().__init__(config)
        self.okt = Okt()

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        if not text:
            return []

        words_with_pos = self.okt.pos(text, norm=True, stem=True)

        tokens = []
        running_offset = 0
        for word, pos_tag in words_with_pos:
            try:
                word_offset = text.index(word, running_offset)
                # Token 객체 생성 시 end 파라미터도 필요합니다.
                token = Token(word, word_offset, end=(word_offset + len(word)), data={"pos": pos_tag}) # <<< Token 생성 시 end 추가
                tokens.append(token)
                running_offset = word_offset + len(word)
            except ValueError:
                running_offset += len(word)

        return tokens