from typing import List, Optional, Set

from terminusdb_client.woqlschema.woql_schema import (
    DocumentTemplate,
    EnumTemplate,
    HashKey,
    TaggedUnion, # what is this?
    WOQLSchema,
)

seshat_schema = WOQLSchema()

# first define ScopedValue classes and associated enums for Polity properties

# useful enums
class enum_EpistemicState(EnumTemplate):
    _schema = seshat_schema
    absent = ()
    present = ()

# NOTE Gavin had admin levels as an enum with one,two,three, etc. as values
# but we want them as integers constrained from 0 to 8-10 or so. JSB? How to do that?

class enum_Confidence(EnumTemplate):
    _schema = seshat_schema
    # JSB? Is this the way you declare xsd types of a property?
    suspected = 'xsd:boolean' # is the value (typically unknown) provided by an RA versus an expert
    disputed  = 'xsd:boolean' # is this one of several disputed values {}?
    inferred  = 'xsd:boolean' # is the value inferred somehow?
    
class ScopedValue(DocumentTemplate):
    _schema = seshat_schema
    unknown = 'xsd:boolean' # is the (typed) value explicitly unknown?
     # JSB? is using Set[] the right way to do this?
     # since we can have disputed and inferred at the same time I think so
     # JSB? also is the syntax really using [] and not ()?  Does python parse that correctly?
    confidence = Set[enum_Confidence]
    dates = 'xsd:gYearRange' # dates to restrict the value to... e.g., Foo: 134BCE-200CE

# Type mixins (boxed classes) for property ScopedValues
# TODO verify capitalization of property names and types
class EpistemicState(DocumentTemplate):
    _schema = seshat_schema
    EpistemicState: enum_EpistemicState

class String(DocumentTemplate):
    '''Any text or sequence of characters'''
    _schema = seshat_schema
    String: 'xsd:string' # or str?

class Integer(DocumentTemplate):
    '''A simple number'''
    _schema = seshat_schema
    Integer: 'xsd:integer'

class IntegerRange(DocumentTemplate):
    '''A simple number or range of integers'''
    _schema = seshat_schema
    IntegerRange: 'xsd:integerRange'

class Decimal(DocumentTemplate):
    '''A decimal number'''
    _schema = seshat_schema
    Decimal: 'xsd:decimal'

class DecimalRange(DocumentTemplate):
    '''A decimal number'''
    _schema = seshat_schema
    DecimalRange: 'xsd:decimalRange'

class gYear(DocumentTemplate):
    '''A particular Gregorian 4 digit year YYYY - negative years are BCE'''
    _schema = seshat_schema
    gYear: 'xsd:gYear'

class gYearRange(DocumentTemplate):
    '''A 4-digit Gregorian year, YYYY, or if uncertain, a range of years [YYYY,YYYY]'''
    _schema = seshat_schema
    gYearRange: 'xdd:gYearRange'


# Define example topic Section/Subsection classes (no properties on these)
class Topic(DocumentTemplate):
    '''Root of topic hierarchy'''
    _schema = seshat_schema
    label = ''
    _subdocument = []

class GeneralInfo(DocumentTemplate):
    _schema = seshat_schema
    label = 'General information variables'
    _subdocument = [Topic]

class SocialComplexity(DocumentTemplate):
    _schema = seshat_schema
    label = 'Social Complexity variables'
    _subdocument = [Topic]

class Military(DocumentTemplate):
    _schema = seshat_schema
    label = 'Miltiary variables'
    _subdocument = [Topic]

class Politics(DocumentTemplate):
    _schema = seshat_schema
    label = 'Political variables'
    _subdocument = [Topic]

# A subsection
class Legal(DocumentTemplate):
    _schema = seshat_schema
    label = 'Legal system variables'
    _subdocument = [Politics]


# Define property scoped values that inherit from 'section' classes
# NOTE: label will be used to parse from csv file strings to the proper class types
# and for pretty display on the website 
# JSB? How do we declare instances with random gensym for names?  How to specify/override @key?

class PeakDate(DocumentTemplate): 
    _schema = seshat_schema
    label = 'Peak date'
    # Format of _subdocument for each seshat property is ScopedValue, then a boxed type, then one or more Topics
    _subdocument = [ScopedValue Date GeneralInfo]

class Duration(DocumentTemplate): 
    _schema = seshat_schema
    label = 'Duration'
    _subdocument = [ScopedValue YearRange GeneralInfo]

class Territory(DocumentTemplate):
    _schema = seshat_schema
    label = 'Polity territory'
    _subdocument = [ScopedValue DecimalRange SocialComplexity]

class ProfessionalMilitary(DocumentTemplate): 
    _schema = seshat_schema
    label = 'Professional military'
    # permits present/absent values
    _subdocument = [ScopedValue EpistemicState Military]

# TODO Need an example to inherit from Legal subsection

# Define properties with a property scoped value or a Set[property scoped value] if uncertainty [] is allowed
class Polity(DocumentTemplate):
    _schema = seshat_schema
    polid: str # the equivalent of 'label'?  JSB? Note use of str, not 'xsd:string'?
    originalID: str # to compare with the old wiki polity page names
    # in order to permit uncertain or disputed values with different dates all seshat properties are Set[]
    peak_date: Set[PeakDate] # typically only one but could be disputed
    duration: Set[Duration]
    territory: Set[Territory]
    professional_military: Set[ProfessionalMilitary]


# define an example instance from our powerpoint slide (slide 7)
# in fact, we'll generate these by parsing the csv file and then constructing or updating a JSON object
# so no use? of the Python constructors with arguments?
# We will be building up a document instance 'patch' (or fetching and patching the whole instance)
# Need to mock this up using our python dictionary scheme...
# These are all instances of some ScopedValue class
peak_date_1 = PeakDate(Date='1761') #string or integer?
duration_1 = Duration(DateRange='[1741,1826]') #string or integer?
territory_1 = Territory(DecimalRange='[60000,80000]',dates='1772')
territory_2 = Territory(DecimalRange='[179000,490000]',dates='1800')
professional_military_1 = ProfessionalMilitary(EpistemicState=enum_EpistemicState.present,inferred=True)
# TODO other examples not on the slide:
# disputed values with inferred
# a suspected unknown
afdurn = Polity(polid='af_durn',originalID='Afdurrn',
                peak_date=[peak_date_1], # are the []'s required for singleton sets?
                duration=[duration_1],
                territory=[territory_1,territory_2], # NOTE alternative data values here
                professional_military=[professional_military_1]
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
