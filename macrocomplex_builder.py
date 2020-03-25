# imports
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from Bio import SeqIO, PDB, pairwise2
from Bio.PDB.Polypeptide import PPBuilder
import argparse, os, sys, UserInteraction
import processInputFiles
import random
import loggingSetup
#import chimera
#from DetectClash import detectClash

class Chain(object):
    """ DESCRIPTION """

    def __init__(self,structure, sequence, file_index, interactions):
        self.__structure = structure
        self.__sequence = sequence
        self.__file_index = file_index
        self.__interactions = interactions

    def get_structure(self):
        return self.__structure

    def get_sequence(self):
        return self.__sequence

    def get_file_index(self):
        return self.__file_index

    def get_interaction(self):
        return self.__interactions

    def __len__(self):
        return len(self.__sequence)

class Complex(object):
    """ DESCRIPTION """

    def __init__(self, structure, chains, pdb_files=False):
        self.__structure = structure
        self.__chains = chains
        self.__pdb_files = pdb_files

    def get_structure(self):
        return self.__structure

    def get_chains(self):
        return self.__chains
    
    def get_pdb_files(self):
        return self.__pdb_files
    
    def calc_z_score(self):
        # how to calculate z_score? 
        return 


#main function that is called when running the script
if __name__ == "__main__":
    """ Macrocomplex builder based on structure superimposition."""

    # obtaining fasta and pdb files

    fasta_files, pdb_files, log = processInputFiles.processInput()


# PARSING OF DATA
# TODO: insert case of empty fasta file
    seq_record_list = []
    for seq in fasta_files:
        for seq_record in SeqIO.parse(seq, "fasta"):
            seq_record_list.append(seq_record)

# TODO: insert case of empty pdb-file
    parser = PDB.PDBParser()
    interact_structure = []
    for pdb_struct in pdb_files:
        interact_structure.append(parser.get_structure(pdb_struct,pdb_struct))
    print("interact structure", interact_structure)
    ppb = PPBuilder()
    chains = []
    for i in range(len(interact_structure)):
            peptide1 = ppb.build_peptides(interact_structure[i])[0]
            # saves the record as a chain object with pdb-file index and sequence
            peptide2 = ppb.build_peptides(interact_structure[i])[1]
            structure1, structure2 = interact_structure[i][0].get_chains()
            chains.append(Chain(structure1, peptide1.get_sequence(), i, peptide2))
            chains.append(Chain(structure2, peptide2.get_sequence(), i, peptide1))

    log.info("PDB interactions processed")
    for i in range(len(chains)):
        print(chains[i])

    # for i in range(len(pdb_files)):
    #     for record in SeqIO.parse(pdb_files[i], "pdb-seqres"):
    #         # saves the record together with the index of the pdb file
    #         chains = chains.append([record,i])

# SEQUENCE ALIGNMENTS

# find the sequences that occur multiple times in pdb files and save all proteins for each structural aln in a separate list
sequences = []
for i in range(len(chains)):
    for m in range(i):
        print("i:", i)
        print("m:", m)
        # just check sequence alignments if sequences are not in the same pair
        if (chains[i].get_file_index() != chains[m].get_file_index()):
            print("Seq1:", chains[i].get_file_index())
            print("Seq2:", chains[m].get_file_index())
            # find the best alignment for two sequences (first element of list of alignments)
            alignment = pairwise2.align.globalxx(chains[i].get_sequence(), chains[m].get_sequence())[0]
            aln_seq_1 = alignment[0]
            aln_seq_2 = alignment[1]
            al_length = len(alignment[0])
            ident = sum(base1 == base2 for base1, base2 in zip(aln_seq_1, aln_seq_2))
            if ident/al_length >= 0.95:
                print("is identical")
                inserted = True
                for similar_seq in sequences:
                    if chains[i] in similar_seq:
                        if chains[m] not in similar_seq:
                            similar_seq.append(chains[m])
                            inserted = False
                            break
                    if chains[m] in similar_seq:
                        if chains[i] not in similar_seq:
                            similar_seq.append(chains[i])
                            inserted = False
                            break
                    if chains[m] in similar_seq and chains[i] in similar_seq:
                        inserted = False
                        break
                if inserted:
                    sequences.append([chains[i], chains[m]])
                print(sequences)
log.info(f"{len(sequences)} homologous chains found")
for i in range(len(sequences)):
    for el in sequences[i]:
        print("elem", i, el.get_file_index())

# HELPER FUNCTIONS

def get_superimpose_options(chain_to_superimpose):
    for similar_seq in sequences:
        if chain_to_superimpose in similar_seq:
            return similar_seq

# search for clashes here
def get_superimpose_options(current_complex, pdb_list):
    for similar_seq in sequences:
        if chain_to_superimpose in similar_seq:
            return similar_seq

# TODO: check both chains of starting complex and combine them to complete complex

# final_complexes = []
# def create_macrocomplex(current_complex, superimpose_chain, threshold):
#     superimpose_options = get_superimpose_options(superimpose_chain)
#     # no other superimposition options -> reached a leaf of the tree
#     if not superimpose_options:
#         # append to list of final complexes
#         return superimpose(superimpose_chain,) 
#      # reach threshold
#     if (threshold == 0):
#         # append to list of final complexes
#         return 
#     for chain_option in superimpose_options:
#         # TODO: combine multiple superimpose options
#         superimposition = superimpose(superimpose_chain, chain_option)
#         created_complex = 
#         current_rmsd = superimpose(superimpose_chain, chain_option)
#         rmsd_threshold = 0
#         if created_complex.rms < rmsd_threshold:
#             if not is_clashing(current_complex, chain_option):
#             #if not is_clashing2(created_complex):
#                 create_macrocomplex(created_complex, chain_option.get_interaction(),threshold-1)


# def create_macrocomplex(current_complex, next_chain, threshold):
#     # gives us the new complex and the according rmsd
#     superimposition = superimpose(superimpose_chain, next_chain)
    
#     superimpose_options = get_superimpose_options(superimposition[0],chains)
#     # new complex has no other superimposition options -> reached a leaf of the tree
#     if not superimpose_options:
#         # append to list of final complexes
#         return superimposition 
#      # reach threshold
#     if (threshold == 0):
#         # append to list of final complexes
#         return superimposition
#     ## add here case for stoichometry
#     if FALSE:
#         return superimposition
    
#     for option in superimpose_options:
#         created_complex = create_macrocomplex(created_complex, option ,threshold-1)
#         current_structure = created_complex[]
#         current_rmsd = created_complex[1]
                


def create_macrocomplex(current_complex, threshold):
    superimpose_options = get_superimpose_options(current_complex[0],pdb_seq)
    best_complex = current_complex
    print("here")
    # starting complex has no superimposition options
    if not superimpose_options:
        # then just return the starting complex
        return best_complex
    else:
        for option in superimpose_options:
            option_complex = superimpose(current_complex[0], option)
            # no other superimposition options for the complex available (leaf)
            # or reached threshold
            # or TODO: ADD STOICHOMETRY option
            if not get_superimpose_options(option_complex, pdb_seq) or \
                (threshold == 0) or \
                    False:
                # if rmsd for option complex is lower than for the current best complex replace it
                if option_complex[1] < best_complex[1]:
                    best_complex = option_complex
            # reach threshold
            else:
                # if we didn't reach the leaf yet, recursive call
                create_macrocomplex(option_complex ,threshold-1)
    return best_complex
        
   
   
def is_clashing(current_complex, chain_to_superimpose):
    backbone = {"CA", "C1\'"}
    model_atoms = [atom for atom in current_complex.get_atoms() if atom.id in backbone]
    chain_atoms = [atom for atom in chain_to_superimpose if atom.id in backbone]
    nsearch = PDB.NeighborSearch(model_atoms) # Generates a neigbour search tree
    clashes = 0
    for atom in chain_atoms:
        clashes += bool(nsearch.search(atom.coord, 1.7))  # If this atom shows clashes, add 1 to the clashes counter
    if clashes/len(chain_atoms) >= 0.03:  # If more than 3% of atoms show clashes return yes
        return True
    else:  # Otherwise return no
        return False

# def is_clashing2(created_complex):
#     clashes = detectClash(created_complex.get_atoms())
#     sum = 0
#     for clashDict in clashes.values():
#         sum += len(clashDict)
#     numClashes = sum/2
#     if numClashes/len() >= 0.03:  # If more than 3% of atoms show clashes return yes
#         return True
#     else:  # Otherwise return no
#         return False


def superimpose(current_complex, chain_b):
    # TODO: only with backbone
    # TODO: check all different positions ??? 

    # get superimposition positions in the current complex
    superimposition_positions = []

    superimp = PDB.Superimposer()
    best_superimposition = None
    best_rmsd = 10
    for chain in superimposition_positions:
        atoms_a = []
        atoms_b = []
        for elem in chain.get_atoms():
            atoms_a.append(elem)
        for elem in chain_b.get_atoms():
            atoms_b.append(elem)
        # setting fixed and moving atoms 
        superimp.set_atoms(atoms_a, atoms_b)
        # apply the superimposition, TODO: think about copy??
        superimposition = superimp.apply(atoms_b) 
        rmsd = superimp.rms
        if rmsd < best_rmsd:
            best_superimposition = superimposition
            best_rmsd = rmsd
    created_complex = Complex(best_superimposition, current_complex.get_chains().append(chain_b))
    return created_complex

# BUILDING UP THE COMPLEX

# start with pdb-file with the most interactions


start_pdb = interact_structure[index][0]
starting_complex = Complex(start_pdb.get_atoms(), )
create_macrocomplex(starting_complex, 100)

# check for DNA 