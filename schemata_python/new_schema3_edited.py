from typing import List, Optional, Set, Union


from terminusdb_client_python.terminusdb_client.woqlschema.woql_schema import (
#from terminusdb_client_python.terminusdb_client.woqlschema.woql_schema import (

    DocumentTemplate,

    EnumTemplate,

    HashKey,

    RandomKey,

    LexicalKey,

    #TaggedUnion, # a disjuction 

    WOQLSchema,

    WOQLClient,

)



from enum import Enum
#from terminusdb_client.woqlclient.woqlClient import WOQLClient
#from terminusdb_client_python.terminusdb_client.woqlclient.woqlClient import WOQLClient

import pprint as pp

import sys

seshat_schema = WOQLSchema()



# first define ScopedValue classes and associated enums for Polity properties



# useful enums

class enum_EpistemicState(EnumTemplate):

    _schema = seshat_schema

    absent = ()

    absent_to_present = ()

    present = ()

    present_to_absent = ()



# Dan points out that there are some other residual possible enumerations around bureaucracy etc

# ('direct', 'widespread', 'infrequent', etc.) but that these will all be converted to present/absent

# and recoded on the wiki before transfer.  So EpistemicState is likely our only data enum



class ScopedValue(DocumentTemplate):

    _schema = seshat_schema

    # Per Gavin, declare key type on the final class, not on mixins

    # _key = RandomKey

    dates: 'xsd:gYearRange' # dates to restrict the value to... e.g., Foo: 134BCE-200CE

    # Confidence qualifiers

    # Semantics: if unknown is True then there will/must be no value set on the BoxedType tagged union

    # If unknown is True, suspected could be set True if it was supplied by an RA

    # and it would be removed (not set to False) once the expert approves

    # otherwise for a 'normal' fact it would have

    # 1) no unknown or suspected property,

    # 2) one of the BoxedType properties

    # 3) optionally one or both of disputed or inferred set

    unknown:   'xsd:boolean' # is the (typed) value explicitly unknown?

    suspected: 'xsd:boolean' # is the value (typically unknown) provided by an RA versus an expert

    disputed:  'xsd:boolean' # is this one of several disputed values {}?

    inferred:  'xsd:boolean' # is the value inferred somehow?



# Type mixins (boxed classes) for property ScopedValues

# TODO verify capitalization of property names and types

class EpistemicState(DocumentTemplate):

    _schema = seshat_schema

    epistemic_state: enum_EpistemicState



class String(DocumentTemplate):

    '''Any text or sequence of characters'''

    _schema = seshat_schema

    string: 'xsd:string' # or str?



class NonNegativeInteger(DocumentTemplate):

    '''A non-negative number'''

    _schema = seshat_schema

    non_negative_integer: 'xdd:nonNegativeInteger'



class Integer(DocumentTemplate):

    '''A simple number'''

    _schema = seshat_schema

    integer: 'xsd:integer'



class IntegerRange(DocumentTemplate):

    '''A simple number or range of integers'''

    _schema = seshat_schema

    integer_range: 'xsd:integerRange'



class Decimal(DocumentTemplate):

    '''A decimal number'''

    _schema = seshat_schema

    decimal: 'xsd:decimal'



class DecimalRange(DocumentTemplate):

    '''A decimal number'''

    _schema = seshat_schema

    decimal_range: 'xsd:decimalRange'



class GYear(DocumentTemplate):

    '''A particular Gregorian 4 digit year YYYY - negative years are BCE'''

    _schema = seshat_schema

    gYear: 'xsd:gYear'



class GYearRange(DocumentTemplate):

    '''A 4-digit Gregorian year, YYYY, or if uncertain, a range of years [YYYY,YYYY]'''

    _schema = seshat_schema

    gYearRange: 'xdd:gYearRange'

# ... define all the rest of the types from boxed_basic_types list







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

# Note: by adding the explicit boxed type class to the supers of the property we can query the schema to

# determine what type it expects.  Self-documenting.

# Note: our look-aside dicts would maintain information that the 'Peak data' Variable from a csv file

# would map to the 'peak_date' property on a Polity

# and that its BoxedType property (on the ScopedValue value instance) is gYearRange

# which requires a (possibly reformed) ValueTo csv string that can be cast to a 'xdd:gYearRange'



# Format of inheritance for each seshat property is ScopedValue, then a boxed type, then one or more Topics

class PeakDate(ScopedValue, GYearRange, GeneralInfo): 

    '''Peak date'''

    _schema = seshat_schema

    _subdocument = []

    _key = RandomKey



class Duration(ScopedValue, GYearRange, GeneralInfo): 

    '''Duration'''

    _schema = seshat_schema

    _subdocument = []

    _key = RandomKey



class Territory(ScopedValue, DecimalRange, SocialComplexity):

    '''Polity territory'''

    _schema = seshat_schema

    _subdocument = []

    _key = RandomKey



class ProfessionalMilitary(ScopedValue, EpistemicState, Military): 

    '''Professional military'''

    _schema = seshat_schema

    _subdocument = []

    _key = RandomKey



# Note singleton name

class Administrative_level(ScopedValue, NonNegativeInteger, Politics): 

    '''Administrative level'''

    _schema = seshat_schema

    _subdocument = []

    _key = RandomKey





# TODO Need an example to inherit from Legal subsection



# Define properties with a property scoped value or a Set[property scoped value] if uncertainty [] is allowed

# marshall values back and forth?

# tuple of Year elements e.g. range 



class Polity(DocumentTemplate):

    _schema = seshat_schema

    _key = LexicalKey("polid")

    polid: str # the equivalent of 'label'?  Note use of str, not 'xsd:string'?

    originalID: str # to compare with the old wiki polity page names

    # in order to permit uncertain or disputed values with different dates all seshat properties are Set[]

    peak_date: Set[PeakDate] # typically only one but could be disputed

    duration: Set[Duration]

    territory: Set[Territory]

    professional_military: Set[ProfessionalMilitary]

    administrative_level: Set[Administrative_level]





# define an example Polity instance from our powerpoint slide (slide 7)

# in fact, we'll generate these by parsing the csv file and then constructing or updating a JSON object

# We will be building up a document instance 'patch' (or fetching and patching the whole instance)

# Need to mock this up using our python dictionary scheme...



# Define all the property values, which are instances of some property class which inherits from ScopedValue

# These will all be instances with random ids

peak_date_1 = PeakDate()

peak_date_1.gYearRange='1761'

# e.g., 1741-1826CE

duration_1 = Duration()

duration_1.gYearRange='[1741,1826]'

# e.g., [60000,80000]:1772; [179000,490000]:1800

territory_1 = Territory()

territory_1.decimal_range='[60000,80000]'

territory_1.dates='1772'



territory_2 = Territory()

territory_2.decimal_range='[179000,490000]'

territory_2.dates='1800'



# e.g., inferred present

professional_military_1 = ProfessionalMilitary()

professional_military_1.epistemic_state = enum_EpistemicState.present

professional_military_1.inferred = True



# a made up example to test disputed,

# e.g, {4:1800; 5:1800}

adm_level1 = Administrative_level()

adm_level1.non_negative_integer = '4'

adm_level1.dates = '1800'

adm_level1.disputed = True



adm_level2 = Administrative_level()

adm_level2.non_negative_integer = '5'

adm_level2.dates='1800'

adm_level2.disputed=True



afdurrn = Polity(polid='af_durn',originalID='Afdurrn',

                peak_date=[peak_date_1], # are the []'s required for singleton sets?

                duration=[duration_1],

                territory=[territory_1,territory_2], # NOTE alternative data values here

                professional_military=[professional_military_1],

                administrative_level=[adm_level1,adm_level2] # NOTE a set of disputed values

                )





client = WOQLClient("https://127.0.0.1:6363/", insecure=True)

client.connect(key="root", account="admin", user="admin")
#client.connect()



exists = client.get_database("majidani_test_seshat", client.account())

if exists:

    client.delete_database("majidani_test_seshat")

client.create_database("majidani_test_seshat") # reset the DB

# Create the schema:

seshat_schema_dict = seshat_schema.to_dict()

#af_dict = afdurrn._to_dict()
pp.pprint(afdurrn._obj_to_dict())
print('xxxxxxxxxxxxxxxxxxxx')

#pp.pprint(seshat_schema_dict) # report the internal form of the full schema

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

    client.insert_document(afdurrn, commit_msg="Commit Afdurn", graph_type= "instance")

except Exception as E:

    print(E.error_obj)

    sys.exit(2)



results = client.get_all_documents(graph_type="instance")

sys.exit(0)

