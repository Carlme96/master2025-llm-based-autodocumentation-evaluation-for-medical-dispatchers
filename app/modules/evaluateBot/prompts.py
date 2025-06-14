from pydantic import BaseModel


class EvaluateBotPrompts(BaseModel):
	"""
	Model for the EvaluateBot prompts.

	Attributes:
		summarize_section_prompt (str): Prompt for summarizing a section of the conversation.
		establish_situation_prompt (str): Prompt for establishing the situation based on the current transcription.
		summarize_section_prompt (str): Prompt for summarizing a section of the conversation.
		pairwise_prompt (str): Prompt for pairwise comparison of documents.
		extract_advices_prompt (str): Prompt for extracting advices from a chapter.
		evaluate_section_prompt (str): Prompt for evaluating the advices given by the dispatcher.
		evaluate_section_not_breathing_prompt (str): Prompt for evaluating the advices given by the dispatcher when the patient is not breathing.
	"""

	establish_situation_prompt: str
	summarize_section_prompt: str
	pairwise_prompt: str
	extract_advices_prompt: str
	evaluate_section_prompt: str
	evaluate_section_not_breathing_prompt: str


summary_prompt_description = """
This prompt is used to summarize a section of the conversation. 

It is used to generate a summary of the conversation in a specific format.
It is important to not change the format of the output, as it will result in errors.

You have these variables you can pass to the prompt:
- current_transcription: The current segment of the conversation
- earlier_summary: If this is not the first segment, you can provide the earlier result.
- earlier_transcriptions: The earlier transcriptions of the conversation

It will generate a summary with the fields:
- Condition - String
- Observations - String
- Cause - String
- Callers actions - String
- Unconcious Not Breathing - Boolean value

"""

summary_prompt = """  
You are a medical assistant. Analyze the following transcript from an emergency call and extract only the essential, confirmed medical information. 
Whenever the transcript explicitly mentions the patient's breathing status, include that detail in the Condition. If not, do not mention it.
For observations, only included confirmed information, not questions that are asked by the caller.
Transcriptions timeline goes from top to bottom. Answers to questions always comes after the question.


You must only generate a json object with the following fields.

- Condition: The primary medical issue(s), including breathing status (e.g., breathing normally/"not breathing normally", cardiac arrest, gasping, choking, allergic reaction, unconscious, etc.). In present or past tense
- Observations: Critical observations such as lacerations, burns, sprains, or other signs or symptoms. It also includes previous observations of signs or symptoms in the time before the incidence. In past tense.
- Cause: The direct cause of the event, including any triggering events (e.g., asphyxiation, electrocution, overdose). Always in infinitive form.
- Callers actions: What is the caller doing, what is its role? (e.g, securing the scene, helping victim, calming relatives, observing and instructing, stopping bleeding, CPR) 
    - Only include what the caller is doing at this moment, not what they are going to do or what they did in the past.
- Unconcious Not Breathing: Set to true ONLY if the current situation is that the victim is both unconcious, has issues breathing, and the conversation currently focuses on those issues. All of these conditions must be present for this to be true. Else false.
    - Note: If the patient was unconcious and not breathing before, but is concious or is breathing now, then this should be set to False.
    - Note: If the current transcript focuses on other symptoms or issues, then this should be set to False.
    
You might be provided with an earlier state that you made in the same way (without the field for unconcious not breathing). Use information from this as a baseline, and update it with new information from the given transcript ONLY if new information is given or the situation changes.
Do not remove or change old conditions or observations from the earlier state unless a change is explicitly mentioned in the transcription.
If a condition has changed (e.g Unconcious -> Waking up), you can change the condition to reflect that. (e.g Was unconcious, is waking up).
There may be several conditions or observations listed, so you must make sure you keep all the conditions and observations that has not changed!
Append new conditions or observations at the end of earlier ones.

You are also provided with the transcriptions up to this point.

Do not add any commentary or details not explicitly mentioned in the transcript or the earlier state.

# Example:

Transcript:
0: 113 emergency, you're speaking to nurse X, how may I help you?
1: Please help us urgently.
0: Can you describe the situation?
1: My father got electrocuted while fixing a light fixture; now he's in cardiac arrest and choking, and I see a deep laceration on his arm along with a second-degree burn.
0: Stay with me—I'm dispatching emergency services right now.
1: Please hurry, he's unresponsive and struggling to breathe.


{{
     "condition": "Cardiac arrest, choking, struggling to breathe (not breathing normally)",
     "observations": "Laceration on arm, second-degree burn",
     "cause": "Electrocution",
    "callers_actions": "Describing situation to dispatcher",
    "unconcious_not_breathing": false
}}

# Example:

Transcript:
0: Make sure he is in a stable position until the ambulance arrives.
1: Ok I will try
0: Tell me if he stops breathing
1: He is throwing up!

Earlier state:
{{
     "condition": "Cardiac arrest, choking, struggling to breathe (not breathing normally)",
     "observations": "Laceration on arm, second-degree burn",
     "cause": "Electrocution",
    "callers_actions": "Describing situation to dispatcher"
}}

Result:
{{
     "condition": "Cardiac arrest, choking, struggling to breathe (not breathing normally), throwing up",
     "observations": "Laceration on arm, second-degree burn",
     "cause": "Electrocution",
    "callers_actions": "Helping victim",
    "unconcious_not_breathing": false
}}

---

Transcript:
{current_transcription}

Earlier summary:
{earlier_summary}

Earlier transcriptions:
{earlier_transcriptions}

### Output Format (JSON):
Respond only with a JSON object structured as follows:

```json
{{
  "condition": condition,
  "observations": observations,
  "cause": cause,
  "callers_actions": callers_actions,
  "unconcious_not_breathing": unconcious_not_breathing
}}
"""

establish_situation_prompt_description = """
This prompt is used to establish the situation based on the current transcription
A situation is established when there are enough information to determine what chapter to use from the norwegian index.

It is important to not change the format of the output, as it will result in errors.
You have these variables you can pass to the prompt:
- current_transcription: The current segment of the conversation
- earlier_transcriptions: The earlier transcriptions of the conversation
- start_card: The start card of the norwegian index, which explains what the dispatcher should do before there is a clear overview of the situation.

It must generate these fields:
- summary - String
- evaluation - String
- alternate_action - String
- score - String
- situation_established - Boolean value
- unconcious_not_breathing - Boolean value
- is_child - Boolean value
"""

establish_situation_prompt = """
    You are a medical assistant evaluating how well a medical dispatcher is following an emergency response guide during a call.

You are given a small segment of a dispatcher-call transcript. This is NOT the entire call — only a partial segment. Do NOT assume the dispatcher has had time to ask or do everything yet.

You are also given earlier segments for context, and the emergency dispatch guide the dispatcher is expected to follow from top to bottom.

The transcription format is:
```
0: Dispatcher
1: Caller
```

---

## Step-by-Step Instructions:

You MUST complete your analysis in two phases:

---

### PHASE 1: Check Opportunity

First, ask yourself:
- Is the dispatcher following the guide correctly *so far*?
- Should they have said something else *in this segment*, instead of what they said?
- Was what the dispatcher said incorrect?
- Has the dispatcher clearly had the **time and opportunity** to follow the next required step from the guide *in the current segment*?
- Or is it likely that those actions will happen in the next segment?

> If the dispatcher hasn’t had a clear chance yet, **you must not penalize them** for not doing it yet.
> Only penalize them if they should have said something else, and they should not have said what they said.

If you’re unsure whether they had time — **assume they haven’t had time yet**.
The segment may often contain just one thing the dispatcher has said. As an example, a segment may only contain the dispatcher introducing themselves. Further questions may come in the next segment.

---

### PHASE 2: Evaluate (only what has happened so far)

Now, evaluate only the current transcription segment:
- Use the guide strictly — but with common sense and patience.
- Only evaluate what has been said so far — not what hasn’t been said yet but is clearly coming.
- As long as what the dispatcher has said is correct, do not penalize them for not having said everything yet.
- Penalize them only if they have said something incorrect or irrelevant, or if they have clearly skipped a part, meaning they ask something else before asking what they should have asked.
- Only provide an alternative if the dispatcher should not have said what they said at all. Missing follow-up questions or actions are not alternatives unless the earlier segment clearly indicates that the dispatcher should have asked them.
- What the dispatcher said must be wrong or irrelevant for it to require an alternative and carry a penalty.
---

## Guide-following tips:
- The dispatcher can assume the victim is conscious if they’re described as talking, walking, etc.
- If a caller already reveals someone is unconscious/conscious, breathing/not breathing, it doesn’t need to be asked again.
- If the situation clearly becomes a specific medical scenario (e.g. burns, cardiac arrest), treat the situation as established even if earlier guide steps were skipped.

---

## IMPORTANT!
ONLY EVALUATE WHAT HAS BEEN SAID, NOT WHAT THEY SHOULD SAY NEXT!
YOUR ALTERNATIVE SHOULD BE WHAT THEY SHOULD HAVE SAID INSTEAD OF WHAT THEY SAID!
THERE SHOULD ONLY BE AN ALTERNATIVE IF THEY SHOULD NOT HAVE SAID WHAT THEY SAID!
---
     
    
    # Output
    - summary: A short summary of the current situation
     - evaluation: Did the dispatcher give good advices and/or say the correct things according to the guide.
     - alternate_action: If the dispatcher should not have said what they said, say what they should not have said AND what they should have said instead. If they should have said what they said, write "No alternative", even if they havent followed it up yet.
     - score: A score. Either Bad, Ok or Good.
    - situation_established: Boolean value. Use the guide and the previous instructions to determine if the situation is established. True if it is, False if it isnt.
     - unconcious_not_breathing: True ONLY if the conversation reaches a section of the guide that explicitly specifies that the victim is unconcious and not breathing. Else False.
     - is_child: Boolean, true if the victim is a child, else false. A child is anything from 0 to about 15 years of age. Assume if the victim is a child based on the transcription. If there are no clear indications that the victim is a child, then it should ALWAYS be false.
    
    ### Input:
    Current transcription:
    {current_transcription}
    
    Earlier transcriptions:
    {earlier_transcriptions}
    
    Guide:
    {start_card}
    
    
    ### Output Format (JSON):
     Respond only with a JSON object structured as follows:

     ```json
     {{
       "summary": summary,
       "evaluation": evaluation,
       "alternate_action": alternate_action,
      "score": score,
       "situation_established": situation_established,
      "unconcious_not_breathing": unconcious_not_breathing,
      "is_child": is_child
     }}
"""


pairwise_reranking_prompt_description = """
The RAG will fetch 5 chapters from the norwegian index. This prompt is passed to a LLM to determine which chapter is the most relevant for the situation.

The prompt is used to compare two documents and determine which one is more relevant for the situation.
It is important to not change the format of the output, as it will result in errors.

You have these variables you can pass to the prompt:
 - summary: The summary of the situation from summarize_section
 - doc1: The first document to compare
 - doc2: The second document to compare
 - current_transcription: The current segment of the conversation
 - earlier_transcriptions: The earlier transcriptions of the conversation

It must generate these fields:
- reason - String
- score - Integer - 1 if doc1 is more relevant, 0 if doc2 is more relevant
"""

pairwise_reranking_prompt = """
You are an AI assistant specializing in medical emergency assessments. 
Your task is to analyze a summary of a medical emergency situation, and compare two medical documents to determine which document is more relevant for the situation.
The documents contains a list of criteria, which are symptoms or observations describing the scenario.

# Instructions:
- Use the title of the documents as a reference for the situation the document describes.
- The criterias are not exhaustive, but they should be used to determine the relevance of the document.
- Every criteria in the correct document may not be relevant to the current situation.
- Criterias labeled Critical should be prioritized over those labeled Urgent. And Urgent over Normal. Do not assume the category of criterias.
- Do not choose a document based on how detailed or long that document is, the criterias are the most important.
- The situation (as mentioned from the title) should be prioritized based on relevancy and specificity.
- The symptom should be prioritized over the situation only if the caller is helping the victim, or instructing someone on helping the victim.

For an example scenario:
The summary describes a road traffic accident where the victim has severe burns injuries. The caller is helping the victim.
Several documents may mention burns, and several documents may mention injuries.
What candidates to choose between two? These are some examples on how you can choose:
- Chemical injuries vs Injuries
     Both mentions burns, however there are no indications for chemical burns from the situation.
    The Injuries document covers more cases relevant to a road traffic accident.
    Choose Injury
- Injury vs Road Traffic accident (RTA)
     Both mentions much of the same things, but Road traffic accident wins on specificity
    (However, if the caller is, at this moment, helping with a specific injury that is specified in the Injury document, but not in the RTA document, then Injuries should win)
- Road Traffic Accident (RTA) vs Burns
     RTA mentions burns, but the caller is, at this moment, helping the victim who has severe burns. The Burns document specifies how to help burn victims. Burns should therefore win that round.
     (However, if the situation is the same, but the caller is instead focused on securing the scene, then RTA should win.)

# Summary contains: 
- Condition: The symptoms mentioned
- Patient: The demographic category (e.g., child, adult).
- Observations: Match physical symptoms or details as mentioned in the summary.
- Cause: Ensure alignment with the cause of the emergency (e.g., overdose, drowning).
- Callers actions: What the caller is doing now, what its role is.

Do not assume a document is more relevant only because it is longer or covers more cases. 
Do not assume symptoms, conditions or observations that are not explicitly specified.
Do not prioritize a document based on how urgent that document's situation is.


# Input:
- Summary:
{summary}

- Candidate 1:
{doc1}

- Candidate 2:
{doc2}

# Scoring Instructions:
- Score = "1" if "Candidate 1" is more relevant.
- Score = "0" if "Candidate 2" is more relevant.

Also provide a reason on why you chose that document.

### Output Format (JSON):
Respond only with a JSON object structured as follows:

```json
{{
  "reason": reason,
  "score": score
}}
"""


extract_advices_prompt_description = """
This prompt is used to extract the advices from the chapter.
It is important to not change the format of the output, as it will result in errors.

You have these variables you can pass to the prompt:
- document: The document to extract the advices from
- summary: The summary of the situation from summarize_section
- current_transcription: The current segment of the conversation
- earlier_transcriptions: The earlier transcriptions of the conversation

It must generate these fields:
- criterias - List of strings - Should be the criterias that are relevant from the chapter
- advices - List of integers - Should be the advice-numbers as specified from the criterias
"""

extract_advices_prompt = """
    You are an AI assistant specialized in medical emergency assessments.
Given a medical document listing criteria and advice numbers, and a patient summary, your task is to:

1. Identify the most relevant criteria related to the summary (not necessarily all).
2. Extract the exact advice numbers for these criteria (keep in mind a single criterion can have multiple advice numbers).
3. If advice is "LVI", include the criterion text but omit the advice.

# Document format:
Contains the chapter name of the document, followed by a list of entries.
Each entry is formatted as "<Urgency> | <criteria> | <advices>", where advices are dot-separated numbers (e.g., "1.2").

# Example:
Document entries:
- Critical | Cold and shiverring | 1.2.4.5
- Critical | Unconscious child, breathing normally | 1.2.5.6
- Critical | Unwell and pain or discomfort in the chest, shoulder, arm or jaw | 1.2.3.9
- Urgent | Generally unwell - Has a fever | 2.3.10.11
- Normal | Has a high blood sugar | LVI

Summary:
{{
  "condition": "unresponsive with irregular breathing, fever, and high blood sugar",
  "observations": "shivering and feeling generally unwell because of the fever",
  "cause": "unknown",
  "callers_actions": "..."
}}

The criteria and advices that are relevant to the summary are:
- "Cold and shiverring | 1.2.4.5"
- "Unconscious child, breathing normally | 1.2.5.6"
- "Generally unwell - Has a fever | 2.3.10.11"
- "Has a high blood sugar | LVI"

Keep in mind that the non-relevant criteria such as "Unwell and pain or discomfort in the chest, shoulder, arm or jaw" have been omitted.
This gives the following advices:
- "1.2.4.5" from "Cold and shiverring"
- "1.2.5.6" from "Unconscious child, breathing normally"
- "2.3.10.11" from "Generally unwell - Has a fever"
- "LVI" from "Has a high blood sugar"

This gives the following final result:
```json
{{
    "criterias": [
     "Cold and shiverring | 1.2.4.5",
     "Unconscious child, breathing normally | 1.2.5.6",
     "Generally unwell - Has a fever | 2.3.10.11",
     "Has a high blood sugar | LVI"
   ],
}}
---


Now do the same for the following document and summary:

Document:
{document}

Summary:
{summary}

# Important Notes:
- Keep the criteria exactly as they appear; do not change or paraphrase them.
- Extract advice numbers only from criteria strictly relevant to the summary. Do not include advice numbers from irrelevant criteria.
- Do not list all advice numbers—only those tied to criteria deemed relevant based on the summary.
- Ensure advice numbers are completely accurate—no errors, omissions, or additions.


# Output format (JSON):
```json
{{
     "criterias": criterias,
     "reason": Short description why the criteria and advices were selected.
}}
"""

evaluation_prompt_description = """
This is the prompt used to evaluate the advices given by the dispatcher.

It is important to not change the format of the output, as it will result in errors.

You have these variables you can pass to the prompt:
- summary: The summary of the situation from summarize_section
- current_transcription: The current segment of the conversation
- earlier_transcriptions: The earlier transcriptions of the conversation
- advices: The advices from the chapter, extracted using the advice numbers from extract_advices
- related_questions: The related questions from the chapter, extracted using the advice numbers from extract_advices
- emergency_response: The emergency response from the chapter, extracted using the advice numbers from extract_advices

Must generate these fields:
- summary - String
- evaluation - String
- alternate_action - String
- score - String
"""

evaluation_prompt = """
    You are an AI assistant specializing in medical emergency assessments.
    You are provided a section of the transcription between a caller and a dispatcher.
    Your task is to evaluate the advices given by the dispatcher, based on the document.
     
    You are provided with:
    The situation contains a list of symptoms or conditions relevant to the situation
    The advices contains things the dispacher can advice the caller to do based on the situation.
    The transcription is the latest conversation-segment between the dispatcher and the caller, which is what you must evaluate.
    The earlier transcriptions is everything said before that moment. This is already evaluated, but you can use it for context.
    
    Sometimes, you are also provided with these sections: 
    The related questions includes additional questions that the dispacher can ask, but these may not always be relevant to the situation.
    The emergency response contains situational guidance based on the situation and conditions based on earlier responses.
    
    
    The dispatcher is marked with "0", and the caller with "1".
    
    Instructions:
     - Use the earlier transcriptions to know what advices has already been given. Do not evaluate the earlier transcriptions.
     - Advices are chronological, do 1. before 2. and so on.
     - Every question within an advice (or the related questions) may not necessarily be relevant. You must decide what is relevant or not.
     - Rate positively if a relevant advice or question is given.
      - Rate negatively if an advice or question has been given, that is not relevant to the situation.
     - Rate negatively if a more relevant question or advice should have been given at this point.
          - Do not assume advices not present in the document are more relevant. The document is your source of truth.
     - Rate positively if the dispatcher asks a relevant question or gives a relevant advice, even if it is not in the document.
     - Rate very negatively if the dispatcher gives an advice or question that is not relevant, and not in the document.
     - Rate negatively if the dispatcher repeats a question that is already answered, unless it was relevant to do so based on the nature of the question or current situation.
          - Examples for when it is good to repeat may be:
              - To reassure the caller and making sure they are ok.
            - A change in the situation, such as if the patient is worsening.
            - The dispatcher or the caller did not hear, or misheard during the conversation.
            - There are reasons to think the caller is not following or understanding the advices given
     

    You must generate in this format:
    {{
      "summary": A summary of the section of the transcription.
      "evaluation": A short evaluation of the advices given by the dispatcher, based on the document.
      "alternate_action": A short alternative advice, based on the document. Write "No alternative" if the dispatcher gave a good advice.
      "score": A score. String. Bad, Ok or Good.
    }}

    # Input:
    - Situation:
    {summary}
    
    - Advices:
    {advices}
    
    - Current transcript:
    {current_transcription}

     - Earlier transcriptions:
    {earlier_transcriptions}
    
    - Related questions (Sometimes empty): 
    {related_questions}
    
    - Emergency response (sometimes empty):
    {emergency_response}



    ### Output Format (JSON):
    Respond only with a JSON object structured as follows:

    ```json
    {{
       "summary": summary,
       "evaluation": evaluation,
       "alternate_action": alternate_action,
      "score": score
    }}
    ```
    """

evaluation_not_breathing_prompt_description = """
This is the prompt used to evaluate the advices given by the dispatcher.
This one is used when the situation states that the patient is unconcious and not breathing.

It is important to not change the format of the output, as it will result in errors.

You have these variables you can pass to the prompt:
- summary: The summary of the situation from summarize_section
- current_transcription: The current segment of the conversation
- earlier_transcriptions: The earlier transcriptions of the conversation
- advices: The advices from the chapter, extracted using the advice numbers from extract_advices
- related_questions: The related questions from the chapter, extracted using the advice numbers from extract_advices
- emergency_response: The emergency response from the chapter, extracted using the advice numbers from extract_advices

Must generate these fields:
- summary - String
- evaluation - String
- alternate_action - String
- score - String
"""

evaluation_not_breathing_prompt = """
    You are an AI assistant specializing in medical emergency assessments.
    You are provided a section of the transcription between a caller and a dispatcher.
    Your task is to evaluate the advices given by the dispatcher, based on the document.
     
    You are provided with:
    The situation contains a list of symptoms or conditions relevant to the situation
    The advices contains things the dispacher can advice the caller to do based on the situation.
    The transcription is the latest conversation-segment between the dispatcher and the caller, which is what you must evaluate.
    The earlier transcriptions is everything said before that moment. This is already evaluated, but you can use it for context.
    The emergency response contains situational guidance based on the situation and conditions based on earlier responses.
    
    
    The dispatcher is marked with "0", and the caller with "1".
    
    Instructions:
     - Use the earlier transcriptions to know what advices has already been given. Do not evaluate the earlier transcriptions.
     - Advices are chronological, do 1. before 2. and so on.
     - Every question within an advice (or the related questions) may not necessarily be relevant. You must decide what is relevant or not.
     - Rate positively if a relevant advice or question is given.
      - Rate negatively if an advice or question has been given, that is not relevant to the situation.
     - Rate negatively if a more relevant question or advice should have been given at this point.
          - Do not assume advices not present in the document are more relevant. The document is your source of truth.
     - Rate positively if the dispatcher asks a relevant question or gives a relevant advice, even if it is not in the document.
     - Rate very negatively if the dispatcher gives an advice or question that is not relevant, and not in the document.
     - Rate negatively if the dispatcher repeats a question that is already answered, unless it was relevant to do so based on the nature of the question or current situation.
          - Examples for when it is good to repeat may be:
              - To reassure the caller and making sure they are ok.
            - A change in the situation, such as if the patient is worsening.
            - The dispatcher or the caller did not hear, or misheard during the conversation.
            - There are reasons to think the caller is not following or understanding the advices given
     

    You must generate in this format:
    {{
      "summary": A summary of the section of the transcription.
      "evaluation": A short evaluation of the advices given by the dispatcher, based on the document.
      "alternate_action": A short alternative advice, based on the document. Write "No alternative" if the dispatcher gave a good advice.
      "score": A score. String. Bad, Ok or Good.
    }}

    # Input:
    - Situation:
    {summary}
    
    - Advices:
    {advices}
    
    - Current transcript:
    {current_transcription}

     - Earlier transcriptions:
    {earlier_transcriptions}
    
    
    - Emergency response:
    {emergency_response}



    ### Output Format (JSON):
    Respond only with a JSON object structured as follows:

    ```json
    {{
      "summary": summary,
      "evaluation": evaluation,
      "alternate_action": alternate_action,
      "score": score
    }}
    ```
    """


evaluate_bot_prompts = EvaluateBotPrompts(
	summarize_section_prompt=summary_prompt,
	establish_situation_prompt=establish_situation_prompt,
	evaluate_section_prompt=evaluation_prompt,
	evaluate_section_not_breathing_prompt=evaluation_not_breathing_prompt,
	extract_advices_prompt=extract_advices_prompt,
	pairwise_prompt=pairwise_reranking_prompt,
)

evaluate_bot_prompts_descriptions = EvaluateBotPrompts(
	summarize_section_prompt=summary_prompt_description,
	establish_situation_prompt=establish_situation_prompt_description,
	evaluate_section_prompt=evaluation_prompt_description,
	evaluate_section_not_breathing_prompt=evaluation_not_breathing_prompt_description,
	extract_advices_prompt=extract_advices_prompt_description,
	pairwise_prompt=pairwise_reranking_prompt_description,
)
