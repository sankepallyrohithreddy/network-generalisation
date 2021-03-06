
import matplotlib.pyplot as plt
from shortest_path_class import *
from common import *
db = sys.argv[1];
table_e = 'cleaned_ways'
table_v = 'cleaned_ways_vertices_pgr'

sp = ShortestPath(db);

d = {}
d["db"] = db;
d["table_e"] = table_e
d["table_v"] = table_v
conn = psycopg2.connect(database=d['db'], user="rohithreddy", password="postgres", host="127.0.0.1", port="5432")
d['conn'] = conn;

cur = conn.cursor()

equal = 0;
non_equal = 0;

# Generating vertexx pairs
print "Generating vertex pairs...."
d['num_pairs'] = 1000
actual_path_costs = []
diff_cost = []
random_query = "SELECT id FROM %s ;"
cur.execute(random_query, (AsIs(d['table_v']), ));
rows = cur.fetchall()

levels = [10,20,30,40,50]
count = 0
i = 0
while i < d['num_pairs']:
	pair = [random.choice(rows), random.choice(rows)]
	if count % 10 == 0:
		print count
	query = "INSERT INTO %s(source, target, level, actual_distance, contracted_distance) VALUES(%s, %s, %s, %s, %s)"
	geom_query = "UPDATE %s SET %s = (SELECT ST_UNION(edge_table.the_geom) FROM %s AS edge_table WHERE edge_table.id = ANY(%s)) WHERE source = %s AND target = %s AND level = %s"
	#print pair
	#print "source===,target " , pair[0], pair[1]
	orig_path = sp.get_original_path(pair[0], pair[1])
	orig_edges = orig_path.get_edge_set()
	if len(orig_edges) <= 2 :
		continue
	orig_dist = orig_path.get_path_cost()*111*1000
	cur.execute(query, (AsIs("paths"), pair[0], pair[1], 100, orig_dist, orig_dist))
	cur.execute(geom_query, (AsIs("paths"), AsIs("the_geom"), AsIs(table_e), list(orig_edges), pair[0], pair[1], 100))
	for level in levels:
		#print "level: ", level
		g_path = sp.get_connected_comp_path(pair[0], pair[1], level)
		#print "Path: ", g_path
		g_edges = g_path.get_edge_set()
		if len(g_edges) <= 1:
			continue
		g_dist = g_path.get_path_cost()*111*1000
		cur.execute(query, (AsIs("paths"), pair[0], pair[1], level, orig_dist, g_dist))
		#print list(g_edges)
		cur.execute(geom_query, (AsIs("paths"), AsIs("the_geom"), AsIs(table_e), list(g_edges), pair[0], pair[1], level))
	i += 1
	count += 1
conn.commit()
