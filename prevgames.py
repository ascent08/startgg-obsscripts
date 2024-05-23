import obspython as obs
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

eventId      = 1234567
authKey      = ""
sets         = 15
interval     = 150
sourceName   = ""
vertical     = False

# ------------------------------------------------------------

def update_text():
	global eventId
	global authKey
	global sets
	global interval
	global sourceName
	global vertical

	source = obs.obs_get_source_by_name(sourceName)
	if source is not None:
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

		settings = obs.obs_data_create()
		obs.obs_data_set_string(settings, "text", text)
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)

		obs.obs_source_release(source)

def refresh_pressed(props, prop):
	update_text()

# ------------------------------------------------------------

def script_description():
	return "Displays previous games for a start.gg event in a text source."

def script_update(settings):
	global eventId
	global authKey
	global interval
	global sets
	global sourceName
	global vertical

	eventId      = obs.obs_data_get_int(settings, "eventId")
	authKey      = obs.obs_data_get_string(settings, "authKey")
	interval     = obs.obs_data_get_int(settings, "interval")
	sets         = obs.obs_data_get_int(settings, "sets")
	sourceName   = obs.obs_data_get_string(settings, "source")
	vertical     = obs.obs_data_get_bool(settings, "vertical")

	obs.timer_remove(update_text)

	if eventId != 0 and authKey != "" and sourceName != "":
		obs.timer_add(update_text, interval * 1000)

def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "interval", 150)
	obs.obs_data_set_default_int(settings, "sets", 15)

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_int(props, "eventId", "start.gg Event ID", 100000, 9999999, 1)
	obs.obs_properties_add_text(props, "authKey", "start.gg API Key", obs.OBS_TEXT_PASSWORD)
	obs.obs_properties_add_int(props, "sets", "Number of sets", 5, 40, 1)
	obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 5, 3600, 1)
	obs.obs_properties_add_bool(props, "vertical", "Arrange sets vertically")

	p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_unversioned_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
	return props
