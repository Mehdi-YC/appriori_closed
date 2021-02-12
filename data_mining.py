import sqlite3
import itertools
from collections import defaultdict

class Aporior:
    def __init__(self  ,min_sup ,min_conf , db_file_name ):
        self.min_sup = min_sup
        self.min_conf = min_conf
        self.frquent_itemsets = {}
        self.transactions = self.initialize_transactions(db_file_name)
        #print(self.transactions)
        self.unique_transaction = self.initialize_unique_transaction()
        #print(self.unique_transaction)

    def initialize_transactions(self,db_file_name) :
        with sqlite3.connect(db_file_name) as conn:
            cur  = conn.cursor()
            data= cur.execute("select transactions from  data_table1").fetchall()
        #print(data)
        return data

    #Histogamme des items dans le dataset
    def initialize_unique_transaction(self) :
        transactions = defaultdict(int)
        
        for transaction in self.transactions :
            for char in transaction[0] :
                    transactions[char] += 1
        #print(f"transactions -> {transactions}")
        return transactions

    def display_data(self) :
        print("\nData_set = {} .\n".format(self.transactions))
        print("Unique_Transaction : ")
        for item,sup_count in self.unique_transaction.items() :
            print(f"item : {item} , sup_count : {sup_count} ")
        print("_________________________\n")

    def Aporior_algorithm(self) :
        L = []
        for char in self.unique_transaction.keys() :
                if self.unique_transaction[char] >=self.min_sup[0] :
                    #self.frquent_itemsets[char]={"sup_count" : self.unique_transaction[char]}
                    L.append(char)  
        while L != []:
            for i in range( len(self.min_sup)-1):
                print(f"database {i+2}")
                with sqlite3.connect(db) as conn:
                    cur  = conn.cursor()
                    nt_transactions = [i[0] for i in cur.execute(f"SELECT transactions from data_table{i+2}").fetchall()]
                    print(f"nt_transactions -> {nt_transactions}")
                    L2 = []
                    for itemset in L:
                        counter = 0
                        for tr in nt_transactions:
                            if itemset in tr:
                                counter+=1
                            #print(f' tr {tr}| itermset : {itemset}  -> counter : {counter} | support : {self.min_sup[i+1]} | take it : {counter >=self.min_sup[i+1]}')
                        if counter >=self.min_sup[i+1]:
                            self.frquent_itemsets[itemset] ={"sup_count" : 1 }  
                            L2.append(itemset)
                L = L2
                print(f"new L -> {L}")
            C = apriori_gen(L)
            L = []
            print(f"L -> {L}")
        print(f"last frequent itemsets : {self.frquent_itemsets.keys()}")
    def _close(self) :
        list1 = []
        list2 = []
        item_sets = sorted(self.frquent_itemsets.keys(),key = len ,reverse=True)
        for item in item_sets :
            if len(item) == len(item_sets[0]) :
                self.frquent_itemsets[item]['closed'] = True
                list1.append(item) 
            else :
                closed  = True
                if  len(list1[0]) - len(item) == 2 :
                    list1 = list2
                    list2 = []    
                list2.append(item)
                for super_set in list1 :               
                    if set(item) <= set(super_set) :

                        if self.frquent_itemsets[item]['sup_count'] == self.frquent_itemsets[super_set]['sup_count'] :
                            closed = False
                    if not closed :
                        break
                self.frquent_itemsets[item]['closed'] = closed   

    def association_rules(self) :
        association_rules_data = defaultdict(list)
        item_sets = sorted(self.frquent_itemsets.keys(), key=len, reverse=True)
        closed = [item for item in item_sets if self.frquent_itemsets[item]['closed']]
        for item in closed:
            if len(item) > 1 :
                item_subsets = all_subsets(item)
                next(item_subsets)
                for subset in item_subsets :
                    if len(subset) == len(item) :
                        break
                    l = set(item) - set(subset)
                    conf =  self.frquent_itemsets[item]['sup_count']/self.frquent_itemsets[''.join(subset)]['sup_count']
                    association_rules_data[item].append(conf_data(item,subset ,self.frquent_itemsets[item]['sup_count'] ,conf ,self.min_conf ,conf>=self.min_conf ))
        return association_rules_data

    def display_all_data(self):
        self.display_data()
        print("Min_Support = {} .\n".format(self.min_sup))
        items = sorted(self.frquent_itemsets.keys(),key = len )
        for item in items:
            if self.frquent_itemsets[item]["closed"]:
                print("SET = {} : SUP = {} >= min_sup({}) ".format(set(item),self.frquent_itemsets[item]["sup_count"],self.min_sup))
        write_association_rules(self.association_rules()) 

def all_subsets(ss):
  return itertools.chain(*map(lambda x: itertools.combinations(ss, x), range(0, len(ss)+1)))
#////////////////////////////////////////////////////////////////////////////////////
def is_frequent(item_sets , canditate , min_sup ) :
    count = 0
    #print("here")
    #print(item_sets,canditate,min_sup)
    #print(canditate)
    #print(min_sup)
    for transaction in item_sets :
        if set(canditate) <= set(transaction[0] ) :
            count += 1
    if count >= min_sup :
        return True,count
    return False,count
#////////////////////////////////////////////////////////////////////////////////////
def has_infrequent_itemset(canditate , frequent_itemsets) :
    canditate_subsets = itertools.combinations(
        canditate, len(canditate)-1)  # get_subsets
    for subset in canditate_subsets:
        if ''.join(subset) not in frequent_itemsets :
            return True
    return False
#////////////////////////////////////////////////////////////////////////////////////
def apriori_gen(frequent_itemsets) :
    length = len(frequent_itemsets[0])
    if length ==1 :
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :
                canditate = sorted([frequent_itemsets[i],frequent_itemsets[j]])
                yield ''.join(canditate)
    else : 
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :            
                if frequent_itemsets[i][:length-1] == frequent_itemsets[j][:length-1] :
                    canditate = set(frequent_itemsets[i]).union(set(frequent_itemsets[j]))
                    canditate = sorted(canditate)
                    if not has_infrequent_itemset(''.join(canditate) , frequent_itemsets) :
                        yield ''.join(canditate)                   

def write_association_rules(association_rules_data, filename='associations.txt'):
    with open(filename,'w') as file :
        for item in association_rules_data.keys() :
            file.write('Item : {} \n'.format((item)))
            for rule in association_rules_data[item] :
                file.writelines(rule)
                file.write('\n')
            file.write('______________________________________________\n')

def conf_data(item , subset ,item_sup , conf , min_conf , case ) :
    p1 = ''.join(['{} ^ '.format(char) for char in subset[:-1]])+'{}'.format(subset[-1])
    p2_items = sorted(set(item)-set(subset))
    p2 = ''.join(['{} ^ '.format(char) for char in p2_items[:-1]])+'{}'.format(p2_items[-1])
    return '\tR: {} --> {} \t\t\n'.format(p1,p2),'\tConfidence = SC({})/SC({}) = {} / {} = {}% {} min_conf({}%) \n'.format(item,''.join(subset),item_sup,item_sup/conf,conf*100,'>=' if case else '<',min_conf*100),'\tR is Selected.\n' if case else '\tR is Rejected.\n'



db="training_datatset.db"
with sqlite3.connect(db) as conn:
    print("__________Database infos_________________\n")
    cur  = conn.cursor()
    num_of_tables = cur.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name like '%data_table%'").fetchall()[0][0]
    data = [cur.execute(f"select count(transactions) from  data_table{i+1}").fetchall()[0][0] for i in range(num_of_tables)]
    for i,display in enumerate(data):
        print(f"number of transactions in table n:{i+1} -> {display}")
    print(f"*total transactiosn in the database -> {sum(data)}")
    print("_________________________________________\n")


table_number = num_of_tables+1
while table_number >num_of_tables:
    try:
        table_number=int(input("select the number of tables you want to use : "))
    except:
        table_number = num_of_tables+1


minsupi=[int(input(f"enter the min sup fot the table {i+1} : ")) for i in range(table_number)]
#APPRIOR(NUM OF TABLES , LIST OF SUP FOR EACH ONE, CONFIDENCE , DB)
obj = Aporior(minsupi,0.4,db)
obj.Aporior_algorithm()
obj._close()
obj.display_all_data()