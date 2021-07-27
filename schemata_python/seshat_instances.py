from typing import List, Optional, Set
from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    TaggedUnion, # an 'enum'
    WOQLSchema,
)

seshat_schema = WOQLSchema()
# first define ScopedValue classes and associated enums for Polity properties
# useful enums
# added random comment to test commit
class enum_EpistemicState(EnumTemplate):
    _schema = seshat_schema
    absent = ()
    present = ()
# Type mixins (boxed classes) for property ScopedValues
# TODO verify capitalization of property names and types
# Define the boxed types as a TaggedUnion

class BoxedType(TaggedUnion):
    _schema = seshat_schema
    epistemic_state: enum_EpistemicState
    string: 'xsd:string' # or str? Any text or sequence of characters
    integer: 'xsd:integer' # A simple number
    integer_range: 'xsd:integerRange'  # A simple number or range of integer
    decimal: 'xsd:decimal' # A decimal number
    decimal_range: 'xsd:decimalRange' # A decimal number or a range of decimals
    gYear: 'xsd:gYear' # A particular Gregorian 4 digit year YYYY - negative years are BCE
    gYearRange: 'xdd:gYearRange' # A 4-digit Gregorian year, YYYY, or if uncertain, a range of years [YYYY,YYYY]
    nonNegativeInteger: "xsd:nonNegativeInteger" # A simple number greater than 0.

# ... define all the rest of the types from boxed_basic_types list
# JSB? By inheriting the BoxedType TaggedUnion with all the other properties declared here
# does the system ensure there will be only one of the 'typed' properties asserted on any particular instance of ScopedValue?

class ScopedValue(DocumentTemplate, BoxedType):
    _schema = seshat_schema
    dates = 'xsd:gYearRange' # dates to restrict the value to... e.g., Foo: 134BCE-200CE
    # Confidence qualifiers
    # Semantics: if unknown is True then there will/must be no value set on the BoxedType tagged union
    # If unknown is True, suspected could be set True if it was supplied by an RA
    # and it would be removed (not set to False) once the expert approves
    # otherwise for a 'normal' fact it would have:
    # 1) no unknown or suspected property,
    # 2) one of the BoxedType properties
    # 3) optionally one or both of disputed or inferred set
    unknown   = 'xsd:boolean' # is the (typed) value explicitly unknown?
    suspected = 'xsd:boolean' # is the value (typically unknown) provided by an RA versus an expert
    disputed  = 'xsd:boolean' # is this one of several disputed values {}?
    inferred  = 'xsd:boolean' # is the value inferred somehow?

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
class Legal(Politics): # Inherit from Politics as a subsection, not DocumentTemplate

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

class PeakDate(ScopedValue, GeneralInfo):
    _schema = seshat_schema
    label = 'Peak date'

    # Format of _subdocument for each seshat property is ScopedValue, then a boxed type, then one or more Topics
    _subdocument = []


class Duration(ScopedValue, GeneralInfo):

    _schema = seshat_schema
    label = 'Duration'
    _subdocument = []


# DGP edit Duration, Territory etc as PeakDate above


class Territory(ScopedValue, SocialComplexity):
    _schema = seshat_schema
    label = 'Polity territory'
    _subdocument = []


class ProfessionalMilitary(ScopedValue, Military):

    _schema = seshat_schema
    label = 'Professional military'
    _subdocument = []


# Note singleton name

class Administrative_level(ScopedValue, Politics):
    _schema = seshat_schema
    label = 'Administrative level'
    _subdocument = []

# TODO Need an example to inherit from Legal subsection
# Define properties with a property scoped value or a Set[property scoped value] if uncertainty [] is allowed
# marshall values back and forth?

# tuple of Year elements e.g. range


class Polity(DocumentTemplate):
    _schema = seshat_schema
    polid: str # the equivalent of 'label'?  JSB? Note use of str, not 'xsd:string'?
    originalID: str # to compare with the old wiki polity page names
    # in order to permit uncertain or disputed values with different dates all seshat properties are Set[]
    peak_date: Set[PeakDate] # typically only one but could be disputed
    duration: Set[Duration]
    territory: Set[Territory]
    professional_military: Set[ProfessionalMilitary]
    administrative_level: Set[Administrative_levels]



# define an example instance from our powerpoint slide (slide 7)
# in fact, we'll generate these by parsing the csv file and then constructing or updating a JSON object
# so no use? of the Python constructors with arguments?
# We will be building up a document instance 'patch' (or fetching and patching the whole instance)
# Need to mock this up using our python dictionary scheme...
# These are all instances of some ScopedValue class


peak_date_1 = PeakDate(Date='1761') #string or integer?
# e.g., 1741-1826CE
duration_1 = Duration(DateRange='[1741,1826]') #string or integer?
# e.g., [60000,80000]:1772; [179000,490000]:1800
territory_1 = Territory(DecimalRange='[60000,80000]',dates='1772')
territory_2 = Territory(DecimalRange='[179000,490000]',dates='1800')


# e.g., inferred present


professional_military_1 = ProfessionalMilitary(EpistemicState=enum_EpistemicState.present,inferred=True)
# a made up example to test disputed,


# e.g, {4:1800; 5:1800}


adm_level1 = Administrative_level(nonNegativeInteger='4',dates='1800',disputed=True)
adm_level2 = Administrative_level(nonNegativeInteger='5',dates='1800',disputed=True)
afdurn = Polity(polid='af_durn',originalID='Afdurrn',
                peak_date=[peak_date_1], # are the []'s required for singleton sets?
                duration=[duration_1],
                territory=[territory_1,territory_2], # NOTE alternative data values here
                professional_military=[professional_military_1],
                administrative_level=[adm_level1,adm_level2] # NOTE a set of disputed values
                )


client = WOQLClient("http://127.0.0.1:6363/")
client.connect()


exists = client.get_database("test_seshat")
if exists:
    client.delete_database("test_seshat")
client.create_database("test_seshat") # reset the DB

# Create the schema:
seshat_schema_dict = seshat_schema.to_dict()

pp.pprint(seshat_schema_dict) # report the internal form of the full schema

try:
    client.insert_document(seshat_schema_dict,
                           commit_msg="Creating the schema",
                           graph_type="schema")
except Exception as E:
    print(E.error_obj)
    sys.exit(1)


# Add a single instance

pp.pprint(afdurrn.to_dict()) # report the internal form of the instance

try:
    client.insert_document(afdurn, commit_msg="Commit Afdurn", graph_type= "instance")

except Exception as E:
    print(E.error_obj)
    sys.exit(2)

results = client.get_all_documents(graph_type="instance")
sys.exit(0)

