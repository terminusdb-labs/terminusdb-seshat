from typing import List, Optional, Set

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    TaggedUnion,
    WOQLSchema,
)

from terminusdb_client.woqlclient.woqlClient import WOQLClient

import pprint as pp

# from woql_schema import WOQLSchema, Document, Property, WOQLObject

seshat_schema = WOQLSchema()

# class MyObject(DocumentTemplate):
#     _schema = my_schema
#
#
# class MyDocument(DocumentTemplate):
#     _schema = my_schema


class GeneralVariables(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    alternative_name: Set[str]
    language: str


class EpistemicState(EnumTemplate):
    _schema = seshat_schema
    absent = ()
    present = ()
    unknown = ()
    inferred_absent = ()
    inferred_present = ()

class AdministrativeLevels(EnumTemplate):
    """levels: An example of hierarchy for a state society
    could be (5) the overall ruler, (4) provincial/regional governors,
    (3) district heads, (2) town mayors, (1) village heads.
    Note that unlike in settlement hierarchy, here you code
    people hierarchy.
    Do not simply copy settlement hierarchy data here.
    For archaeological polities, you will usually code as 'unknown',
    unless experts identified ranks of chiefs or officials independently
    of the settlement hierarchy.
    Note: Often there are more than one concurrent administrative hierarchy.
    In the example above the hierarchy refers to the territorial government.
    In addition, the ruler may have a hierarchically organized central
    bureaucracy located in the capital. For example, (4)the overall ruler,
    (3) chiefs of various ministries, (2) mid-level bureaucrats,
    (1) scribes and clerks.
    In the narrative paragraph detail what is known about both hierarchies.
    The machine-readable code should reflect the largest number
    (the longer chain of command)."""

    _schema = seshat_schema
    five = ()
    four = ()
    three = ()
    two = ()
    one = ()


class HierarchicalComplexity(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    admin_levels: 'AdministrativeLevels'

class SpecializedBuildingsPolityOwned(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    bridges: 'EpistemicState'


class Information(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    articles: 'EpistemicState'

class SocialComplexityVariables(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    hierarchical_complexity: HierarchicalComplexity
    specialized_buildings_polity_owned: Optional['SpecializedBuildingsPolityOwned']
    information: Information

class MilitaryTechnologies(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    breastplates: 'EpistemicState'
    atlatl: 'EpistemicState'
    battle_axes: 'EpistemicState'

class WarfareVariables(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    military_technologies: MilitaryTechnologies

class Polity(DocumentTemplate):
    _schema = seshat_schema
    name: str
    general_variables: GeneralVariables
    social_complexity_variables: SocialComplexityVariables
    warfare_variables: WarfareVariables

class Confidence(EnumTemplate):
    _schema = seshat_schema
    inferred = ()
    suspected = ()

section = GeneralVariables()
section.language = "Latin"

codebook = Polity()
codebook.name = "Code book"
codebook.general_variables = section

print(codebook._obj_to_dict())


hierarch_complex = HierarchicalComplexity(admin_levels = AdministrativeLevels.five)
info = Information(articles = EpistemicState.present)
social_complex = SocialComplexityVariables(
    hierarchical_complexity = hierarch_complex,
    information=info
)
war_var = WarfareVariables(
    military_technologies=MilitaryTechnologies(atlatl=EpistemicState.present,
                                               battle_axes=EpistemicState.present,
                                               breastplates=EpistemicState.present)
)
gen_var = GeneralVariables(alternative_name = ["Sadozai Kingdom", "Last Afghan Empire"])
affdurrn = Polity(name="AfDurrn",
                  social_complexity_variables=social_complex,
                  general_variables=gen_var,
                  warfare_variables=war_var)

pp.pprint(affdurrn._obj_to_dict())


client = WOQLClient("http://127.0.0.1:6363/")
client.connect()

exists = client.get_database("test_seshat")
print(exists)

if exists:
    client.delete_database("test_seshat")

client.create_database("test_seshat")

print(client._auth())
stuff = seshat_schema.to_dict()
pp.pprint(stuff)
try:
    client.insert_document(seshat_schema.to_dict(),
                           commit_msg="I am checking in the schema",
                           graph_type="schema")
except Exception as E:
    print(E.error_obj)


client.insert_document(affdurrn, commit_msg="checking if it is working", graph_type= "instance")
results = client.get_all_documents(graph_type="instance")
print(list(results))

