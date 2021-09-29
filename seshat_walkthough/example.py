from terminusdb_client.woqlschema import WOQLSchema, DocumentTemplate, LexicalKey, EnumTemplate, HashKey, RandomKey
from terminusdb_client import WOQLClient
from typing import List, Optional, Set
from enum import Enum
import pprint as pp


user = "dani"
team = "PAOK-test"  # My team name.
endpoint = f"https://cloud.terminusdb.com/PAOK-test/"
client = WOQLClient(endpoint)

client.connect(user=user, team=team, use_token=True)

exists = client.get_database("test_seshat")
if exists:
    client.delete_database("test_seshat")
client.create_database("test_seshat")  # reset the DB

seshat_schema = WOQLSchema()


class EpistemicState(EnumTemplate):
    '''Enumeration Type'''
    _schema = seshat_schema
    absent = ()
    absent_to_present = ()
    present = ()
    present_to_absent = ()

# ... define all the rest of the types from boxed_basic_types list


class IntegerRange(DocumentTemplate):
    '''A simple number or range of integers'''
    _schema = seshat_schema
    integer_range: Set[int]


class DecimalRange(DocumentTemplate):
    '''Decimal number range'''
    _schema = seshat_schema
    decimal_range: Set[float]


class GYear(DocumentTemplate):
    '''A particular Gregorian 4 digit year YYYY - negative years are BCE'''
    _schema = seshat_schema
    g_year: int


class GYearRange(DocumentTemplate):
    '''A 4-digit Gregorian year, YYYY, or if uncertain, a range of years [YYYY,YYYY]'''
    _schema = seshat_schema
    g_year_range: Set[int]


class Boolean(Enum):
    _schema = seshat_schema
    value: bool


class ScopedValue(DocumentTemplate):
    _schema = seshat_schema
    dates: Optional['GYearRange']  # dates to restrict the value to... e.g., Foo: 134BCE-200CE
    # Confidence qualifiers
    # Semantics: if unknown is True then there will/must be no value set on the BoxedType tagged union
    # If unknown is True, suspected could be set True if it was supplied by an RA
    # and it would be removed (not set to False) once the expert approves
    # otherwise for a 'normal' fact it would have
    # 1) no unknown or suspected property,
    # 2) one of the BoxedType properties
    # 3) optionally one or both of disputed or inferred set
    unknown: Optional[bool]  # is the (typed) value explicitly unknown?
    # is the value (typically unknown) provided by an RA versus an expert
    suspected: Optional[bool]
    disputed: Optional[bool]  # is this one of several disputed values {}?
    inferred: Optional[bool]  # is the value inferred somehow?
# Type mixins (boxed classes) for property ScopedValues
# TODO verify capitalization of property names and types

# Define example topic Section/Subsection classes (no properties on these)


class Topic(DocumentTemplate):
    '''Root of topic hierarchy'''
    _schema = seshat_schema
    _abstract = []


class GeneralInfo(Topic):
    '''General information variables'''
    _schema = seshat_schema
    _abstract = []


class SocialComplexity(Topic):
    '''Social Complexity variables'''
    _schema = seshat_schema
    _abstract = []


class Military(Topic):
   '''Miltiary variables'''
   _schema = seshat_schema
   _abstract = []


class Politics(Topic):
    '''Political variables'''
    _schema = seshat_schema
    _abstract = []
# A subsection


class Legal(Politics):  # Inherit from Politics as a subsection, not DocumentTemplate
    '''Legal system variables'''
    _schema = seshat_schema
    _abstract = []

# NOTE: label will be used to parse from csv file strings to the proper class types
# and for pretty display on the website
# JSB? How do we declare instances with random gensym for names?  How to specify/override @key?
# Note: our look-aside dicts would maintain information that the 'Peak data' Variable from a csv file

# would map to the 'peak_date' property on a Polity
# and that its BoxedType property (on the ScopedValue value instance) is gYearRange
# which requires a (possibly reformed) ValueTo csv string that can be cast to a 'xdd:gYearRange'


class PeakDate(DocumentTemplate):
    '''Peak date

    attribute
    ======================
    peak_date: integer'''
    _schema = seshat_schema
    # Format of _subdocument for each seshat property is ScopedValue, then a boxed type, then one or more Topics
    _subdocument = []
    peak_date: int


class Duration(ScopedValue, GeneralInfo):
    _schema = seshat_schema
    label = 'Duration'
    _subdocument = []
    duration: 'GYearRange'


class TerritoryValue(SocialComplexity):
    _schema = seshat_schema
    label = 'Polity territory'
    _subdocument = []
    territory_range: 'DecimalRange'
    territory_date: 'ScopedValue'


class ProfessionalMilitaryValue(Military):
    _schema = seshat_schema
    label = 'Professional military'
    _subdocument = []
    epistemic_state: 'EpistemicState'
    scope: 'ScopedValue'


class AdministrativeLevelValue(Politics):
    _schema = seshat_schema
    label = 'Administrative level'
    _subdocument = []
    _key = RandomKey
    dates: 'GYearRange'
    disputed: 'ScopedValue'
    value: int


class Territory(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    territory: List['TerritoryValue']


class AdministrativeLevels(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    administrative_levels: List['AdministrativeLevelValue']

# is professional military likely to have more than one values?
# if not there is no need for a list.


class ProfessionalMilitary(DocumentTemplate):
    _schema = seshat_schema
    _subdocument = []
    administrative_levels: List['ProfessionalMilitaryValue']

# TODO Need an example to inherit from Legal subsection
# Define properties with a property scoped value or a Set[property scoped value] if uncertainty [] is allowed
# marshall values back and forth?
# tuple of Year elements e.g. range


class Polity(DocumentTemplate):
    _schema = seshat_schema
    #_key = LexicalKey("polid")
    polid: str  # the equivalent of 'label'?  JSB? Note use of str, not 'xsd:string'?
    _key = LexicalKey(["polid"])
    originalID: str  # to compare with the old wiki polity page names
    # in order to permit uncertain or disputed values with different dates all seshat properties are Set[]
    peak_date: 'PeakDate'  # typically only one but could be disputed
    duration: 'Duration'
    territory: 'Territory'
    professional_military: 'ProfessionalMilitary'
    admin_levels: 'AdministrativeLevels'

seshat_schema.commit(client, commit_msg="Adding Schema")


p_d = PeakDate()
p_d.peak_date = 1761

dur_range = GYearRange()
dur_range.g_year_range = {1741, 1826}
dur = Duration()
dur.duration = dur_range


territory_1 = TerritoryValue()
territory_1.territory_range = DecimalRange(decimal_range={6000, 8000})
territory_1.territory_date = ScopedValue(
    date=GYearRange(g_year_range={1772, }))

territory_2 = TerritoryValue()
territory_2.territory_range = DecimalRange(decimal_range={17900, 49000})
territory_2.territory_date = ScopedValue(
    date=GYearRange(g_year_range={1800, }))

territory_list = Territory()
territory_list.territory = [territory_1, territory_2]

section = ScopedValue()
section.inferred = True

professional_military_1 = ProfessionalMilitaryValue(epistemic_state=EpistemicState.present,
                                                    scope=section)

professional_military_list = [professional_military_1]

adm_scoped_dispute_true = ScopedValue()
adm_scoped_dispute_true.disputed = True

adm_level1 = AdministrativeLevelValue(
    value=4, dates=[GYearRange(g_year_range={1800, })], disputed = adm_scoped_dispute_true)
adm_level2 = AdministrativeLevelValue(
    value=5, dates=GYearRange(g_year_range={1800, }), disputed=adm_scoped_dispute_true)

admin_level_list = AdministrativeLevels()
admin_level_list.administrative_levels = [adm_level1, adm_level2]


afdurn = Polity(polid='af_durn', originalID='Afdurrn',
                peak_date=p_d, duration=dur,
                territory=territory_list,
                professional_military=professional_military_1,
                admin_levels=admin_level_list)
pp.pprint(afdurn._obj_to_dict())

client.insert_document(afdurn, commit_msg=f"Inserting data")
