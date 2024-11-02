from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import time

eventId      = 1234567
authKey      = ""
sets         = 15
interval     = 150
vertical     = False

# ------------------------------------------------------------

while True:
	headers = {'Authorization': 'Bearer ' + authKey}
	transport = AIOHTTPTransport(url="https://api.start.gg/gql/alpha", headers=headers)
	client = Client(transport=transport, fetch_schema_from_transport=True)

	pastsets = gql(
		"""
		query PastSets($eventId: ID!, $page: Int!, $setsPerPage: Int!) {
			event(id: $eventId) {
				sets(
					page: $page,
					perPage: $setsPerPage,
					filters: {
						state: 3
					}
				){
					nodes {
						slots {
							entrant {
								id
								name
							}
						}
						winnerId
					}
				}
			}
		}
		"""
	)

	params = {
		"eventId": eventId,
		"page": 1,
		"setsPerPage": sets,
	}

	text = ""
	seperator = "  |  "
	if vertical:
		seperator = "\n"
	nodes = client.execute(pastsets, variable_values=params)
	nodes = nodes['event']['sets']['nodes']
	for i in range(len(nodes)):
		player1 = nodes[i]['slots'][0]['entrant']['name']
		player1Id = nodes[i]['slots'][0]['entrant']['id']
		player2 = nodes[i]['slots'][1]['entrant']['name']
		player2Id = nodes[i]['slots'][1]['entrant']['id']
		winnerId = nodes[i]['winnerId']
		if '|' in player1:
			player1 = player1.split(' | ',1)[1]
		if '|' in player2:
			player2 = player2.split(' | ',1)[1]
		if player1Id == winnerId:
			gameString = player1 + " def. " + player2 + seperator
		elif player2Id == winnerId:
			gameString = player2 + " def. " + player1 + seperator
		else:
			gameString = player1 + " vs " + player2 + seperator
		text = text + gameString
	if text == "":
		text = "No previous games!"

	f = open("prevgames.txt", "w")
	f.write(text)
	f.close

	time.sleep(interval)
