from pydantic import BaseModel
from typing import Optional
import json
from open_dictionary.llm.llm_client import get_chat_response


instruction = """
你是一位顶级的词典编纂专家、语言学家，以及精通中日双语的教育家。你的任务是读取并解析一段来自 Wiktionary 的、结构复杂的 JSON 数据，然后将其转化为一份清晰、准确、对中文学习者极其友好的结构化中文词典条目。

**核心任务：**
根据下方提供的输入JSON（包含日语词汇数据），严格按照【输出格式定义】生成一个唯一的、完整的 JSON 对象作为最终结果。不要输出任何解释、注释或无关内容。

---

**【输出格式定义】**

请生成一个包含以下键 (key) 的 JSON 对象：

1.  `word`: (string) 日文单词本身（汉字、平假名或片假名）。
2.  `pos`: (string) 词性（如名词、动词、形容词等）。
3.  `pronunciations`: (object) 一个包含发音方式和音频文件的对象：
    *   `ipa`: (string) 国际音标。直接从输入JSON的 `sounds` 数组中提取 `ipa` 字段的值。
    *   `natural_phonics`: (string) 自然读音。根据假名或汉字读音，生成一个对初学者友好的读音提示，用假名表示。例如 "東京" -> "とうきょう"。
    *   `ogg_url`: (string) OGG音频文件链接。从输入JSON的 `sounds` 数组中查找并提取 `ogg_url` 字段的值。如果不存在，则返回 `null`。
4.  `forms`: (array of strings) **词形变化**。遍历输入JSON的 `forms` 数组，将每个词形 (`form`) 及其标签 (`tags`) 组合成一个易于理解的中文描述字符串。例如：`"行きます (敬语/丁寧語)"`。
5.  `concise_definition`: (string) **简明释义**。在分析完所有词义后，用一句话高度概括该单词最核心、最常用的1-2个中文意思。
6.  `detailed_definitions`: (array) **详细释义数组**。遍历输入JSON中 `senses` 数组的每一个对象，为每个词义生成一个包含以下内容的对象：
    *   `definition_en`: (string) **英文原义**。从输入JSON的 `glosses` 数组中，提取出**最具体、最完整**的那个英文释义。如果数组中包含一个概括性标题和一个具体释义，请**选择那个具体的释义**。
    *   `definition_cn`: (string) **中文阐释**。此项是核心，请遵循以下原则：
        *   **解释而非翻译**：用**通俗、自然、易懂**的中文来解释该日语词汇的核心含义。
        *   **捕捉精髓**：要抓住该词义的**使用场景、语气（如敬语、口语、书面语）和细微差别**。
        *   **文化背景**：适当说明日语特有的文化内涵和使用习惯。
        *   **避免直译**：请**避免生硬的、字典式的直译**。目标是让中文母语者能瞬间理解这个词义的真正用法。
    *   `example`: (object) **为该词义创作一个全新的例句**，包含：
        *   `ja`: (string) 一个**简单、现代、生活化**的日文例句，使用合适的敬语级别，清晰地展示当前词义的用法。**绝对不要使用**输入JSON中提供的复杂或古老的例句。
        *   `cn`: (string) 上述日文例句的对应中文翻译。
7.  `derived`: (array of objects) **派生词/复合词**。遍历输入JSON的 `derived` 数组，为其中的**每个单词**生成一个包含以下内容的对象：
    *   `word`: (string) 派生词本身。
    *   `definition_cn`: (string) 对该派生词的**简明中文定义**。
8.  `etymology`: (string) **词源故事**。读取输入JSON中的 `etymology_text` 字段，将其内容翻译并**转述**成一段流畅、易懂的中文。说明其起源语言（如古日语、汉语、英语等）和含义的演变过程，像讲故事一样。如果涉及汉字，说明汉字的演变和意义。

---

**【示例 1】**

**输入JSON:**
`{"word": "走る", "pos": "verb", "forms": [{"form": "走ります", "tags": ["polite", "present"]}, {"form": "走った", "tags": ["past"]}, {"form": "走って", "tags": ["te-form"]}], "senses": [{"glosses": ["To run; to move quickly on foot."]}, {"glosses": ["To flee; to escape."]}], "sounds": [{"ipa": "/haɕiɾu/", "ogg_url": "url"}], "derived": [{"word": "走者"}, {"word": "走れ"}], "etymology_text": "From Old Japanese *pay- ('to fly, to jump'), from Proto-Japanese *paya."}`

**你的JSON输出:**
{
  "word": "走る",
  "pos": "verb",
  "pronunciations": {
    "ipa": "/haɕiɾu/",
    "natural_phonics": "はしる",
    "ogg_url": "url"
  },
  "forms": [
    "走ります (丁寧語)",
    "走った (过去式)",
    "走って (て形)"
  ],
  "concise_definition": "奔跑；逃跑。",
  "detailed_definitions": [
    {
      "definition_en": "To run; to move quickly on foot.",
      "definition_cn": "指人或动物用双脚快速移动的动作，强调速度。日常使用频率很高的基础动词。",
      "example": {
        "ja": "私は每天朝公園を走ります。",
        "cn": "我每天早上在公园跑步。"
      }
    },
    {
      "definition_en": "To flee; to escape.",
      "definition_cn": "逃跑、逃离某地的意思。多用于紧急或危险情况下。",
      "example": {
        "ja": "泥棒は看到了んで走った。",
        "cn": "小偷看到警察就逃跑了。"
      }
    }
  ],
  "derived": [
    {
      "word": "走者",
      "definition_cn": "跑步者，赛跑运动员。"
    },
    {
      "word": "走れ",
      "definition_cn": "走る的命令形，表示命令或祈使。"
    }
  ],
  "etymology": "该词源自古代日语的 *pay-（意为'飞翔，跳动'），最终源于原始日语 *paya。从古至今核心含义一直围绕着'快速移动'这一概念。"
}

---

**【示例 2】**

**输入JSON:**
`{"word": "おもてなし", "pos": "noun", "forms": [{"form": "おもてなし", "tags": ["honorific"]}], "senses": [{"glosses": ["Hospitality; entertainment of guests."]}, {"glosses": ["The act of providing exceptional service to others."]}], "sounds": [{"ipa": "/omotenɕi/", "ogg_url": "url"}], "derived": [{"word": "もてなし"}, {"word": "おもてなしする"}], "etymology_text": "From Old Japanese, from もと (moto, 'origin') + なて (nate, 'to treat, to handle') + the honorific prefix お- (o-)."}`

**你的JSON输出:**
{
  "word": "おもてなし",
  "pos": "noun",
  "pronunciations": {
    "ipa": "/omotenɕi/",
    "natural_phonics": "おもてなし",
    "ogg_url": "url"
  },
  "forms": [
    "おもてなし (敬语)"
  ],
  "concise_definition": "招待，款待；日式优质服务。",
  "detailed_definitions": [
    {
      "definition_en": "Hospitality; entertainment of guests.",
      "definition_cn": "日本特有的招待文化，指主人用心款待客人的行为，体现了日本重视细节和他人感受的待客之道。",
      "example": {
        "ja": "日本のおもてなしは世界でも有名ですね。",
        "cn": "日本的招待文化在世界上也很闻名呢。"
      }
    },
    {
      "definition_en": "The act of providing exceptional service to others.",
      "definition_cn": "超越一般服务标准的、超乎预期的细心周到的服务，强调主动性和用心程度。",
      "example": {
        "ja": "あのホテルのおもてなしには驚いた。",
        "cn": "那家酒店的贴心服务让我很惊讶。"
      }
    }
  ],
  "derived": [
    {
      "word": "もてなし",
      "definition_cn": "款待，招待（较随意的说法）。"
    },
    {
      "word": "おもてなしする",
      "definition_cn": "提供贴心服务，款待。"
    }
  ],
  "etymology": "该词由'もと'（起源）+ 'なて'（对待，处理）+ 敬语前缀'お-'组成，字面意思是'用心对待'。体现了日语中通过敬语表达尊重和重视的文化特色。"
}

---

"""


class Example(BaseModel):
    ja: str
    cn: str


class DetailedDefinition(BaseModel):
    definition_en: str
    definition_cn: str
    example: Example


class DerivedWord(BaseModel):
    word: str
    definition_cn: str


class Pronunciations(BaseModel):
    ipa: str
    natural_phonics: str
    ogg_url: Optional[str] = None


class Definition(BaseModel):
    word: str
    pos: str
    pronunciations: Pronunciations
    forms: list[str]
    concise_definition: str
    detailed_definitions: list[DetailedDefinition]
    derived: list[DerivedWord]
    etymology: str


def define(input_json: dict) -> Definition:
    """Generate a structured dictionary definition from Wiktionary JSON data.

    Args:
        input_json: Dictionary containing Wiktionary data

    Returns:
        Definition object with structured dictionary entry
    """
    input_data = json.dumps(input_json, ensure_ascii=False)
    response = get_chat_response(instruction, input_data)

    return Definition.model_validate_json(response)
