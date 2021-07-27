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
import sys

seshat_schema = WOQLSchema()
# first define ScopedValue classes and associated enums for Polity properties
# useful enums

class enum_EpistemicState(EnumTemplate):
    _schema = seshat_schema
    absent = ()
    present = ()

# Type mixins (boxed classes) for property ScopedValues
# is he using mixin to avoid inheritance ambiguity?
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
    nonNegativeInteger: 'xsd:nonNegativeInteger' # A simple number greater than 0.

# ... define all the rest of the types from boxed_basic_types list
# JSB? By inheriting the BoxedType TaggedUnion with all the other properties declared here
# does the system ensure there will be only one of the 'typed' properties asserted on any particular instance of ScopedValue?

# DGP: in order to inherit from a TaggedUnion I need to add a disjoint process in the system. Do I really need that? Justify.

class ScopedValue(DocumentTemplate):
    _schema = seshat_schema
    dates= 'xsd:YearRange' # dates to restrict the value to... e.g., Foo: 134BCE-200CE
    # e.g. above, from the BoxedType class.
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
# DGP: if the gensym is used to replace the key is it assigned externally? Do we need to have
# a gensym generator where the key is a random gensym? Do I get the question above right?

# Note: our look-aside dicts would maintain information that the 'Peak data' Variable from a csv file would map to the 'peak_date' property on a Polity
# and that its BoxedType property (on the ScopedValue value instance) is gYearRange
# which requires a (possibly reformed) ValueTo csv string that can be cast to a 'xdd:gYearRange'
#DGP: we can have a pre-processing script tht does that-is this the scope of this exercise? If yes should it be included here?


class PeakDate(DocumentTemplate):
    _schema = seshat_schema
    label = 'Peak date'
    # Format of _subdocument for each seshat property is ScopedValue, then a boxed type, then one or more Topics
    _subdocument = [ScopedValue,BoxedType, GeneralInfo]


class Duration(DocumentTemplate):
    _schema = seshat_schema
    label = 'Duration'
    _subdocument = [ScopedValue, BoxedType, GeneralInfo]



class Territory(DocumentTemplate):
    _schema = seshat_schema
    label = 'Polity territory'
    _subdocument = [ScopedValue, BoxedType, SocialComplexity]


class ProfessionalMilitary(DocumentTemplate):

    _schema = seshat_schema
    label = 'Professional military'
    _subdocument = [ScopedValue, BoxedType, Military]
    epist_state: 'enum_EpistemicState'


# Note singleton name

class Administrative_level(ScopedValue, Politics):
    _schema = seshat_schema
    label = 'Administrative level'
    admin_level = Set[ScopedValue]
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
    administrative_level: Set[Administrative_level]



# define an example instance from our powerpoint slide (slide 7)
# in fact, we'll generate these by parsing the csv file and then constructing or updating a JSON object
# so no use? of the Python constructors with arguments?
# We will be building up a document instance 'patch' (or fetching and patching the whole instance)
# Need to mock this up using our python dictionary scheme...
# These are all instances of some ScopedValue class



### Example

#fist lets see how the peak_date behaves. It needs to be an integer or a set.

#peak_date_1 = PeakDate(Date='1761')
# peak_date_1 = '1761' #string or integer? Either- you are looking at a TaggedUnion
# which includes all the definitions

# PeakDate.peak_date = 1761 #Integer
# it also needs to be a set...

#PeakDate.peak_date = [1761, 1236] #Set

# It also works when it is a string.
PeakDate.peak_date = '1761'
# PeakDate.peak_date = ['1761', '1236']

# Now, I want to see how the duration behaves.
# the questions are the same as above (I think)

# e.g., 1741-1826CE
#duration_1 = Duration(DateRange='[1741,1826]') #string or integer?
# Either- you are looking at a TaggedUnion which includes all the definitions
Duration.duration = '[1741,1826]'

#Let's look at the territory

# e.g., [60000,80000]:1772; [179000,490000]:1800
# it seems like i need to construct a set like:[[60000,80000]:1772; [179000,490000]:1800]
# rdfs:range[xsd:Decimal]:xsd:gYear
# it looks like i need to construct classes to parse the definitions
# in the BoxedType class.

Territory.range1 = '[60000,80000]:1772'
Territory.range2 = '[179000,490000]:1800'

# territory_1 = Territory(DecimalRange='[60000,80000]',dates='1772'
# territory_2 = Territory(DecimalRange='[179000,490000]',dates='1800')

# Now let's look at the military


section = ScopedValue()
section.inferred=True
professional_military_1 = ProfessionalMilitary(epist_state = enum_EpistemicState.present,
                                               inferred=True)

# I don't know why inferred does not print. At this stage I have concluded
# that i need to re-write in more detail the BoxedType and ScopedValue classes.

# Administrative levels


afdurn = Polity(polid='af_durn',originalID='Afdurrn',
                 peak_date=PeakDate.peak_date, duration=Duration.duration,
                territory=[Territory.range1, Territory.range2],
                professional_military=professional_military_1
                )

pp.pprint(afdurn._obj_to_dict())



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


