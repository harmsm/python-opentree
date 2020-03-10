# Goal: get the node age for a node in the synth tree
# It is a two step process
# 1) Get the conflict info for a node in synth tree, so we can map synth tree nodes to source tree node.
# 2) Get the node ages of source tree nodes
# 3) expose this info on the otol website

# Example:
# 1.1) Get all trees in phylesystem that have branch lengths proportional to time.

import json
import sys
from opentree import OpenTree

OT = OpenTree()
output = OT.find_trees(search_property="ot:branchLengthMode", value="ot:time")

# 1.2) Get conflict information for each node in source chronograms:
study_id = 'ot_1877' # "ot_864"
tree_id = 'tree3' # "tree1"

output_conflict = OT.conflict_info(study_id = study_id, tree_id= tree_id)
output_conflict.__dict__
output_conflict.response_dict.keys()
print(output_conflict.response_dict["node100"])

conf_info = output_conflict.response_dict

# possible statuses are {'resolved_by', 'conflicts_with', 'supported_by', 'terminal', 'partial_path_of'}
#>>> statuses = set()
#>>> for node in conf_info:
#...     statuses.add(conf_info[node]['status'])

for node in conf_info:
    status = conf_info[node]['status'] # gets the status of each node, see possibilities above
    witness = conf_info[node].get('witness', None) # gets the synthetic node id that is related to the source node
    if status == 'supported_by':
        print("{} {} {} maps to {}".format(study_id, tree_id, node, witness))

# 2) Get ages for those nodes

# We need either:
# 2A) a newick/nexus tree with branch lengths whose node labels match node ids from nexson schema.
## Do peyotl schemas go from nexson tree with branch lengths to newick with branch lengths? Yes.
## Would this process retain node labels from nexson into newick? No...
# If we do:

output = OT.get_tree(study_id, tree_id)
tre = output.response_dict[tree_id]
sys.stdout.write("This tree returns fine, but isn't very meaningful due to lack of otu labels:\n\n {t}\n\n".format(t=tre))

otus = OT.get_otus(study_id)
# print(otus.reponse_dict) # says obkect has no attribute 'response_dict'

tree_newick = OT.get_tree(study_id, tree_id, tree_format="newick", label_format="ot:ottid", demand_success = False)
tree_newick.__dict__
print(tree_newick.tree)

# To newick, we loose the node ids...

# Let's try nexus

tree_nexus = OT.get_tree(study_id, tree_id, tree_format="nexus", label_format="ot:ottid", demand_success = False)
print(tree_nexus.tree)

# node ids are also lost...

# OR,
# 2B) a way to get node heights from a nexson object.

# Get the source tree as nexson:
tree_nexson = OT.get_tree(study_id, tree_id, tree_format="nexson", label_format="ot:ottid", demand_success = False)
tree_nexson.__dict__

## We tried with Dendropy traversal of nexml tree
## we thought this function might work:
## https://dendropy.org/library/treemodel.html?highlight=ages#dendropy.datamodel.treemodel.Tree.internal_node_ages
## but the nexson to nexml conversion is not fully working
## and the node ids are modified by dendropy, so we can't map nodes back to synth tree:
import dendropy
dendropy.datamodel.treemodel.Tree.internal_node_ages

t1 = dendropy.datamodel.treemodel.Tree()
t1.__dict__
s = t1.as_string("nexml")
s.__dict__ # has no attribute __dict__
# MTH created a nexson to DendroPy converter
# You can get the converter method like this:

from opentree import get_object_converter
OC = get_object_converter('dendropy')
# But then I try to run it and I could not figure it out:
OC.tree_from_nexson(tree_nexson, tree_id)
OC.tree_from_newick(tree_newick.tree)
tree_object = OT.get_tree(study_id, tree_id, tree_format="object", label_format="ot:ottid", demand_success = False)
tree_object.__dict__
tree_object.tree
OC.tree_from_newick(tree_object.tree)

# Until I realized it is already implemented in get_tree:
tree_nexson = OT.get_tree(study_id, tree_id, tree_format="nexson", label_format="ot:ottid", demand_success = False)
# And can be extracted with
tree_nexson.response_dict # this has the nexson object
# now read it into dendropy
dendropy.datamodel.treemodel.Tree.internal_node_ages(tree_nexson.response_dict)

# Third alternative:
# Is there a function that gets node heights from a nexson tree object directly, without transforming to nexml?
# Maybe in peyotl?
