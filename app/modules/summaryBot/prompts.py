from pydantic import BaseModel


class SummaryBotPrompts(BaseModel):
	describe_case_prompt: str
	describe_image_prompt: str
	generate_summary_prompt: str
	intention_prompt: str
	transcription_prompt: str


transcription_prompt_description = """
This prompt serves as a explanation of the transcription format used in the data, for the LLM to understand.

A transcription is a written record of the conversation between the dispatcher and the caller.
It includes the dialogue exchanged during the call, capturing the details of the incident as it unfolds.

It follows this format:
	0: Dispatcher’s statements
	1: Caller’s statements

"""

transcription_prompt = """
	Transcripts between a dispatcher (0) and a caller (1). Additionally, an AI may have provided advice (2) to assist the dispatcher in handling the situation effectively.

	The transcript follows this format:
		0: Dispatcher’s statements
		1: Caller’s statements

	Example Transcript:
		0: 911, what's your emergency?  
		1: Hi, I just found someone unconscious in the park. I need help!  
		0: Is the person breathing? Do you feel a pulse?  
		1: I don’t know! I think so, but they’re not moving.  
		0: Can you check if their chest is rising and falling? Try to listen for breathing. If they’re not breathing, I’ll guide you through CPR.  

"""

intention_prompt_description = """
This prompt explains the intention of what you want to report.

It gives context to the LLM about the purpose of the data and how it should be interpreted.

"""

intention_prompt = """
This data pertains to a medical emergency call, such as a 911 dispatch interaction. 
	It includes transcripts of the conversation between the caller and the dispatcher, relevant location details, 
	and snapshots taken from a live video feed when critical visual information appears. 
	The purpose of this data is to document the incident as it unfolds, capturing key medical, environmental, 
	and situational details that may be useful for emergency responders, post-incident analysis, and legal or medical records..
"""


describe_case_prompt_description = """
This prompt is used by an LLM to describe the overall situation.
It used for context to the vision model, such that it can describe the image based on the situation.

You can provide the following variables:
- transcription - contains a transcription between two people
- location - contains the location of the incident
- intention - a prompt explaining the current application
- appname - The name of the application
- incidencetime - The time of the incident
- transcription_prompt - The transcription prompt
"""

describe_case_prompt = """
You are a AI assistant whos job is to describe a case based on partly unstructured data.
							
The result will be used as context for another AI bot, such that it can make informed decisions based on the context.

The result should be objective, and straight to the point, made for other AI bots, not for humans.

It should not just be a list of everything, but a summarization.
You are to be used in several different application settings, based on the input.
The structure of the data is as follows:
transcription - {transcription_prompt}
location - contains the location of the incident
intention - a prompt explaining the current application
appname - The name of the application
incidencetime - The time of the incident


## Input:
- **transcription**: {transcription}
- **location**: {location}
- **intention**: {intention}
- **appname**: {appname}
- **incidencetime**: {incidencetime}
							
## Output
- **Summary:**		

"""


describe_image_prompt_description = """
This prompt is used by the vision model to describe the image.

You can provide the following variables:
- case_description - The case description, which is used to describe the image - from describe_case
"""

describe_image_prompt = """
You are a AI Bot that describes an image for an autodocumenting application.

You are also provided with a context, which describes the current case for autodocumenting.
Also a description of what context the image is taken in.
It may contain info to help you with understanding the context of the image,
however, there are also likely parts of the context that is not relevant.

If parts of the context seems not to be relevant for the image, do not include that part in your reasoning, 
and do not mention it in the result.
Use common sense to decide what is relevant and what is not relevant. 
The context should be connected to the image in some way.

Do not make up anything, try to be objective.
Focus on this image and this image only, based on the context. Do not mention other parts of the context.


Case Description: {case_description}
"""


generate_summary_prompt_description = """
This prompt is used by the LLM to generate a summary of the case.
It is used to generate a summary of the case, based on the data provided.

The result of this LLM is used as the final output of the summary bot.

You can provide the following variables:
- transcription - contains a transcription between two people
- transcription_prompt - The transcription prompt
- location - contains the location of the incident
- intention - a prompt explaining the current application
- appname - The name of the application
- incidencetime - The time of the incident
- image_descriptions - contains a list of descriptions of images taken during the incident
"""


generate_summary_prompt = """
You are a AI assistant whos job is to make a report of a medical incidence.
			
The structure of the data is as follows:
transcription - contains a transcription between two people
location - contains the location of the incident
intention - a prompt explaining the current application
appname - The name of the application
incidencetime - The time of the incident
image_descriptions - contains a list of descriptions of images taken during the incident
							
All fields should only be text, no objects or arrays.
## Input:
- **transcription**: {transcription}
- **location**: {location}
- **intention**: {intention}
- **appname**: {appname}
- **incidencetime**: {incidencetime}
- **image_descriptions**: {image_descriptions}

Make an output in markdown format, see example:
# <A generated name for the incidence>

## Info
**Incidence date:** <Date of incidence>
**Incidence time:** <Time of incidence>
**Location:** <Location of incidence>

## Description
<A short description describing the incidence, who is involved etc>

## Action taken
<A short description on what the dispatcher did and what the caller did>

## Other
**Incidence Type:** <Type of incidence>
**Severity:** <High/Medium/Low>
**Participants:** <Everyone involved, including the patient, dispatcher>		
"""

summary_bot_prompts = SummaryBotPrompts(
	describe_case_prompt=describe_case_prompt,
	describe_image_prompt=describe_image_prompt,
	generate_summary_prompt=generate_summary_prompt,
	intention_prompt=intention_prompt,
	transcription_prompt=transcription_prompt,
)

summary_bot_prompts_description = SummaryBotPrompts(
	describe_case_prompt=describe_case_prompt_description,
	describe_image_prompt=describe_image_prompt_description,
	generate_summary_prompt=generate_summary_prompt_description,
	intention_prompt=intention_prompt_description,
	transcription_prompt=transcription_prompt_description,
)
