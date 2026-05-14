from datetime import datetime
from typing import List, Optional, Union, Dict, Tuple

from pydantic import BaseModel, Field

system_prompt_template_text = """
You are an advanced information-extraction engine.
Your task is to analyze any input text and produce a dense, noise-free knowledge report.
Extract: into 3 sections <#source> Source </#source>, <#entities> old and new entities </#entities>, <#facts> explicit facts <#facts>.
The purpose is to have a full knowledge extraction report with the facts time line that cover both the 
whole context of observation as locally mentioned facts.  

Output in a format with these sections:

(Inside <#source> </#source> tags)
# Source is:
 - description of a source the text comes from
 - source url if available
 - source type (eg. news, blog, social media, etc)

(Inside <#entities> </#entities>)
# Old Entities (old data + description) :
 - Unchanged List of entities from the text with their id, reference, type, etc.
 - Add only description of this old entity, based on provided observation.

(Inside <#entities> </#entities>)
# New entities not listed in text (eg.person-1, customer-1, location-3, etc) examples :
 - People (with roles, traits)
 - Organizations
 - Locations
 - Objects/creations (artwork, documents, etc.)
 - Abstract entities (ideas, groups, topics, concepts, religions, etc.)
 - Semantic description of the entity.

(Inside <#facts> </#facts>)
# Explicit time-lined facts:
 - Verbatim factual information stated in the text.
 - Who did what, when, where, how, etc.
 - If entity is a participant in fact use its name. 
 - The source of the information, either mentioned in text or the text itself.
 - If time or spacial location is provided replace use relevant time or location rather then words use words like: now, current, here, there, upcoming. Use relevant data instead.
 - Each fact should be self containing explanation of what happened placed in time and location if possible 
 - Do not include greetings, explanations, irrelevant commentary, emotional feelings, or any social interaction, just facts. 
 - Causes and effects where clear
 - Extract event type in form of past tense. Extract one word is possible. 
 - etc.
 
 Explicit Facts (how to extract):
 - Extract both general (general fact inferred from text) and specific facts (related to one sentence). Mark them (general) and (specific). Find at least 2 general facts.
 - Facts should be represented one actor predicate and one object if possible. 
 - Fact description should start with the actor (the main entity) of this fact, predicate and objects.
 - Do not include emotional signals tied to entities or events  
 - All time references must be dates not abstract words. eg. for 2024-04-02: Jim signed up for a back-horse riding class yesterday, extract: Jim signed up for a back-horse riding class on 2024-04-01 

 Each Fact should be placed in context:
 * What to include:
  - Verbose description of the event context. It should have everything that is not included in fact but it is context of given fact, some examples of context:
     - Emotional signals tied to entities or events  
     - Location, Organization, Plans, Intentions, etc - If not in the main fact
     - Motivations of entities
     - Information that can be inferred if easily extractable; 
     - etc.
 * Instructions:
  - Be verbose enough to fully explain the context of the event. 
  - Include information not explicitly stated but readily deducible from context. For example relative times. If someone mentions an event (yesterday, previous day, next month, etc) and we know the time of event word then yesterday could be referred in context as concreate data date.  

(Inside <#facts> </#facts>)
# Summary (Dense, No Filler)

A few sentences capturing the core of the text.

> Example text to extract facts from:

Source: Twitter

Entities:
 - <person-1>: person (id=f77e43b11dc688, name=Alex)
 - <person-2>: person (id=94d726b2d7401f, name=Jamie)
 
2024-09-02 12:34:00: Alex: Hey, are you still up for the match on Saturday?
2024-09-02 12:34:01:Jamie: Definitely! I’ve been looking forward to it all week. Who’s playing again—England vs. Spain, right?
2024-09-02 12:34:02:Alex: Yep! A proper big game at Wembley. It’s going to be packed.
2024-09-02 12:34:03:Jamie: Wembley always feels electric on match days. We should get there early just to soak in the atmosphere.
2024-09-02 12:34:05:Alex: For sure. Kickoff’s at 6, so I was thinking we leave around 4:30? Maybe grab food near the stadium.
2024-09-02 12:34:10:Jamie: Works for me. I still remember those insane burgers we had last time.
2024-09-02 12:34:15:Alex: Same! And I’m hoping England actually turn up this time. Spain’s midfield is ridiculous.
2024-09-02 12:34:20:Jamie: True. If England let them control the ball, we’re in trouble.
2024-09-02 12:34:22:Alex: I’m still traumatized from that last 3–0 defeat.
2024-09-02 12:34:25:Jamie: Honestly, same. But Wembley magic might help.
2024-09-02 12:34:34:Alex: Let’s hope so. I’ll swing by your place around 4:15.
2024-09-02 12:34:40:Jamie: Perfect. Face paint or no face paint?
2024-09-02 12:34:45:Alex: Absolutely not.
2024-09-02 12:34:56:Jamie: Coward. See you Saturday.

> Example output report with extended entities and facts

<#source>
 - Description: Casual conversation between two individuals arranging to attend a football match.
 - Twitter (url: x.com, type: social media)
</#source>

<#entities>
# Old Entities (reference, type, traits - always with id):
 - <person-1>: person (id=f77e43b11dc688, name=Alex, description="Alex is friend of Jamie. HE is soccer fan")
 - <person-2>: person (id=94d726b2d7401f, name=Jamie, description="Jamie is soccer fan. Fried of Alex.")
 
# New Entities (type, description):
 - <location-1>: location (type=stadium", description="Wembley Stadium in England"))
 - <location-2>: location (type="property", description="Jamie’s home")
 - <location-3>: location (type="restaurant" description="Food cort at Wembley")
 - <date-1>: date (date="6th of January 2024", description="date of the game")
 - <event-1>: match (type="soccer", description="Soccer math at Wembley Stadium, England against Spain, date=6th of January 2024"))
 - <event-2>: match (type="soccer", description="Soccer math England against Spain last score 3-0"))
 - <country-1>: country (name=England, description="Country located in Europe")
 - <country-2>: country (name=Spain, description="Country located in Europe")
</#entities>

<#facts>
# Facts:
 2024-09-02 12:34:00: (general) 
 Jamie and Alex are fiends and know each other.
  - Actor: <person-1>
  - Event type [knows]
  - Object: [<person-2>]
  - Source: Conversation on Twitter
  - Context: Alex knows Jamie for a long time.
  
 2024-09-02 12:34:00: (general)  
 Jamie and Alex are going to soccer match 
  - Actor: <person-2>
  - Event type [attended]
  - Object: [<location-1>]
  - Source: Conversation on Twitter
  - Context: Match is on Saturday at Wembley Stadium. Jamie is very excited about the match, etc.
  
 2024-09-02 12:34:00: (general) 
 Match is England vs Spain. 
  - Actor: <event-1>
  - Event type [was played]
  - Objects: [<country-1>, <country-2>]
  - Source: Conversation on Twitter
  - Context: England lost to Spain last time 3-0. Inferred tha match was not played at Wembley.
    
 2024-09-02 12:34:01: (specific)
 Jamie confirms participation in an upcoming soccer match at Wembley Stadium on Saturday 
 - Actor: <person-1>
 - Event type [confirmed participation]
 - Object: [<location-1>]
 - Source: Conversation on Twitter
 - Context: Later Alex and Jamie arrange pickup at Jamie's place around 4:15.
    
 2024-09-02 12:34:34 (specific)
 Alex arranges pickup at his place around 4:15.
  - Actor: <person-1>
  - Event type: [arranged pickup]
  - Objects: [<location-1>]
  - Source: Conversation on Twitter
  - Context: Alex and Jamie will stop to grab some food near the stadium.
  
Summary: Alex and Jamie are friends and know each other. They are going to soccer match on Saturday. Match is England vs Spain. Jamie confirms participation in an upcoming soccer match at Wembley Stadium on Saturday. Alex arranges pickup at his place around 4:15.
</#facts>
---

Remember: Strictly focus on maximum information extraction with compact clarity.
"""

system_prompt_entities = """
You are an advanced information-extraction engine that outputs structured data. 
Extract all contained information into a structured object of ExplicitEntities.

Retrieve structured of new and old entities:

# Old Entities (old data + description):
 - Unchanged List of entities from the text with their id, reference, type, etc.
 - Add only description of this old entity, based on provided observation.

# New entities not listed in text (eg.person-1, customer-1, location-3, etc) examples :
 - People (with roles, traits)
 - Organizations
 - Locations
 - Objects/creations (artwork, documents, etc.)
 - Abstract entities (ideas, groups, topics, concepts, religions, etc.)
 - Semantic description of the entity.

# Rules
 - All entities must have ids. Look for IDs in Entities with given identifiers
 - All entities must have reference link.
 - All entities must have types.
 - All entities must have description.

Example output:
ExplicitEntities(
    old_entities=[
     OldEntity(
         id='20599f31fcf51764a522db06a66d0695', 
         reference=Reference(link='person-1'),
         type='person', 
         description='John is a plummer'
     ),
     ...
    ],
    new_entities=[
      NewEntity(
        type='location', 
        reference==Reference(link="location-1"), 
        description='The local area where John and Maria reside.')
      )
    ]
)
"""

system_prompt_facts = """
You are an advanced information-extraction engine that outputs structured data. 
Extract all contained information into a structured object of ExplicitReport.

Retrieve structured
 - Facts with text, context, actor, predicate, objects, source, time, mentioned entities, etc.
 - In facts do not reference entities, use names and any acceptable feature, e.g (Ann, John, woman, etc).  
 - If an entity has no clear name or universally understandable identifier, represent it with an abstract label such as person, organization, location, etc.
 - All ExplicitFact actors and objects must be referenced by their reference link not name or any other property.

Summary:
 - Dense, No Filler

Example output:
facts=[
  ExplicitFact(
    fact='John attended a community meeting.', 
    context="The meeting was about hearing people's worries and how they affect their area, leading John to realize the importance ...", 
    time='2023-01-28 13:17:00', 
    actor=Reference(link='person-1'),
    predicate='attended', 
    objects=[Reference(link='location-1')], 
    source='Chat'
  ) 

summary = John nd Maria had a meeting...
"""

user_prompt_template = """
--- Your job text ---

%s
"""


class Reference(BaseModel):
    link: str = Field(..., description="Reference link.")

    def __str__(self):
        return self.link


class OldEntity(BaseModel):
    id: str = Field(..., description="Entity id.")
    reference: Reference = Field(..., description="Entity reference.")
    type: str = Field(None, description="Entity type, e.g. person, organization, location, etc.")
    description: Optional[str] = Field(None, description="Textual entity description, Who or what is this entity.")

    def format(self) -> str:
        return f"{self.type} id={self.id}, ref={self.reference}, desc={self.description or ''})"


class NewEntity(BaseModel):
    type: str = Field(..., description="Entity type, e.g. person, organization, location, etc.")
    reference: Reference = Field(..., description="Entity reference.")
    description: Optional[str] = Field(None, description="Textual entity description, Who or what is this entity.")

    def format(self) -> str:
        return f"{self.type}, ref={self.reference}, desc={self.description or ''}"


class ExplicitFact(BaseModel):
    fact: str = Field(..., description="Full fact description")
    context: str = Field(..., description="Full event contex")
    time: Optional[Union[str, datetime]] = Field(None, description="Time of event in datetime format if exists")

    actor: Optional[Reference] = Field(None, description="Reference to main actor. Us reference not name.")
    predicate: Optional[str] = Field(..., description="Event predicate")
    objects: Optional[List[Reference]] = Field(None,
                                               description="List of refences related to predicate and actor to objects mentioned in the event. Use references.")

    source: Optional[str] = Field(None, description="Reference to source of the fact")

    def format(self) -> str:
        return (
            f"{self.time}: {self.actor} {self.predicate} "
            f"{(','.join([str(item) for item in self.objects]) if self.objects else '')}\n"
            f"({self.source}) {self.fact}\n"
            f"Context: {self.context}\n"
        )


class ExplicitFacts(BaseModel):
    facts: List[ExplicitFact] = Field(...,description="List of explicit facts with its fact, context, actor, predicate, objects, source, time, etc.")
    summary: str = Field(..., description="Summary of text")

    def format(self):
        output = self.summary
        output += "\n\nFacts:\n"
        output += "\n".join([item.format() for item in self.facts])
        return output


class ExplicitEntities(BaseModel):
    old_entities: List[OldEntity] = Field(..., description="Unchanged list of old entities")
    new_entities: List[NewEntity] = Field(..., description="List of newly identified entities")

    def format(self):
        output = "\n\nOLD Entities:\n"
        output += "\n".join([item.format() for item in self.old_entities])
        output += "\n\nNEW Entities:\n"
        output += "\n".join([item.format() for item in self.new_entities])
        return output

def get_facts_explict_summary_prompt(text: str):
    return (
        system_prompt_template_text,
        user_prompt_template % text,
        .7
    )


def get_explicit_entities_prompt(text: str):
    return (
        system_prompt_entities,
        user_prompt_template % text,
        .7
    )

def get_explicit_facts_prompt(text: str):
    return (
        system_prompt_facts,
        user_prompt_template % text,
        .7
    )