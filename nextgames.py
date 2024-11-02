from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import time

eventId      = 1234567
authKey      = ""
sets         = 15
interval     = 150
sourceName   = ""
vertical     = False

# ------------------------------------------------------------

while True:
	headers = {'Authorization': 'Bearer ' + authKey}
	transport = AIOHTTPTransport(url="https://api.start.gg/gql/alpha", headers=headers)
	client = Client(transport=transport, fetch_schema_from_transport=True)

	futuresets = gql(
		"""
		query FutureSets($eventId: ID!, $page: Int!, $setsPerPage: Int!) {
			event(id: $eventId) {
				sets(
					page: $page,
					perPage: $setsPerPage,
					filters: {
						state: 1
					}
				){
					nodes {
						slots {
							entrant {
								name
							}
						}
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
	setsToPlay = client.execute(futuresets, variable_values=params)
	setsToPlay = setsToPlay['event']['sets']['nodes']
	for i in range(len(setsToPlay)):
		if setsToPlay[i]['slots'][0]['entrant'] == None:
			player1 = "TBD"
		else:
			player1 = setsToPlay[i]['slots'][0]['entrant']['name']
		if setsToPlay[i]['slots'][1]['entrant'] == None:
			player2 = "TBD"
		else:
			player2 = setsToPlay[i]['slots'][1]['entrant']['name']
		if '|' in player1:
			player1 = player1.split(' | ',1)[1]
		if '|' in player2:
			player2 = player2.split(' | ',1)[1]
		gameString = player1 + " vs " + player2 + seperator
		text = text + gameString
	if text == "":
		text = "No upcoming games!"

	f = open("prevgames.txt", "w")
	f.write(text)
	f.close

	time.sleep(interval)

