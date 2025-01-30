from enum import Enum
from typing import Dict, Optional

class CablecastEndpoints(Enum):
    """Cablecast API Endpoints"""
    
    # Live Streaming Endpoints
    LIVE_STREAMS = "/v1/livestreams"
    LIVE_STREAM_STATUS = "/v1/livestreams/{id}/status"
    LIVE_STREAM_STATE = "/v1/livestreams/{id}/state"
    LIVE_STREAM_METRICS = "/v1/livestreams/{id}/metrics"
    LIVE_STREAM_BY_ID = "/v1/livestreams/{id}"
    LIVE_STREAMS_BY_LOCATION = "/v1/livestreams?location={location}"
    LIVE_STREAM_CONFIG = "/v1/livestreamconfigurations/{id}"
    
    # VOD (Video on Demand) Endpoints
    VODS = "/v1/vods"
    VOD_STATUS = "/v1/vodstatuses/{id}"
    VOD_CHAPTERS = "/v1/vods/{id}/chapters"
    VOD_STATS = "/v1/vods/stats"
    
    # Channel Management
    CHANNELS = "/v1/channels"
    CHANNEL_BRANDING = "/v0/channelbrandingstatus"
    
    # Schedule Management  
    SCHEDULE_ITEMS = "/v1/scheduleitems"
    SCHEDULE_ITEM_BY_ID = "/v1/scheduleitems/{id}"
    SCHEDULE_ITEMS_BATCH = "/v1/scheduleitems/batch"
    SCHEDULE_ITEMS_FILTERED = "/v1/scheduleitems?start={start}&end={end}&show={show}&channel={channel}"
    SCHEDULE_GAPS = "/v1/schedule/gaps"
    MANUAL_EVENTS = "/v1/manualevents"
    
    # Device Management
    DEVICES = "/v1/devices"
    DEVICE_BY_ID = "/v1/devices/{id}"
    DEVICE_STATUS = "/v1/devices/{id}/status"
    DEVICE_THUMBNAILS = "/v1/devices/{id}/thumbnails"
    DEVICES_BY_LOCATION = "/v1/devices?location={location}"
    
    # Chaptering Session Endpoints
    CHAPTERING_SESSIONS = "/v1/chapteringsessions"
    CHAPTERING_SESSION_BY_ID = "/v1/chapteringsessions/{id}"
    CHAPTERING_SESSIONS_BY_VOD = "/v1/chapteringsessions?vod={vod}"
    
    # IFrame Endpoints
    IFRAMES = "/v1/iframes"
    IFRAME_BY_ID = "/v1/iframes/{id}"
    IFRAMES_BY_LOCATION = "/v1/iframes?location={location}"
    
    # ShowFile Endpoints
    SHOW_FILES = "/v1/showfiles"
    SHOW_FILE_BY_ID = "/v1/showfiles/{id}"
    SHOW_FILES_BY_SHOW = "/v1/showfiles?show_id={show_id}"
    
    # AssetLog Endpoints
    ASSET_LOGS = "/v1/assetlogs"
    ASSET_LOG_BY_ID = "/v1/assetlogs/{id}"
    ASSET_LOGS_BY_ASSET = "/v1/assetlogs?asset_id={asset_id}&workflowId={workflow_id}"
    
    # Public Site Endpoints
    PUBLIC_SITES = "/v1/publicsites"
    PUBLIC_SITE_BY_ID = "/v1/publicsites/{id}"
    
    # Channel Branding Endpoints
    CHANNEL_BRANDING_STATUS = "/v0/channelbrandingstatus"
    
    # Network Stream Endpoints
    NETWORK_STREAMS = "/v1/networkstreams"
    NETWORK_STREAM_BY_ID = "/v1/networkstreams/{id}"
    NETWORK_STREAMS_BY_LOCATION = "/v1/networkstreams?location={location}"
    
    # VOD Transaction Endpoints
    VOD_TRANSACTIONS = "/v1/vodtransactions"
    VOD_TRANSACTION_BY_ID = "/v1/vodtransactions/{id}"
    VOD_TRANSACTIONS_BATCH = "/v1/vodtransactions/batch"
    
    # Volume Info Endpoints
    VOLUME_INFOS = "/v1/volumeinfos"
    VOLUME_INFO_BY_ID = "/v1/volumeinfos/{id}"
    VOLUME_INFO_STATS = "/v1/volumeinfos/stats"
    
    # Record Events Endpoints
    RECORD_EVENTS = "/v1/recordevents"
    RECORD_EVENT_BY_ID = "/v1/recordevents/{id}"
    RECORD_EVENTS_BY_DATE = "/v1/recordevents?start={start}&end={end}"
    
    # Disposition Endpoints
    DISPOSITIONS = "/v1/dispositions"
    DISPOSITION_BY_ID = "/v1/dispositions/{id}"
    DISPOSITIONS_BY_LOCATION = "/v1/dispositions?location={location}"
    
    # Digital Files Endpoints
    DIGITAL_FILES = "/v1/digitalfiles"
    DIGITAL_FILE_BY_ID = "/v1/digitalfiles/{id}"
    DIGITAL_FILE_LINK = "/v1/digitalfiles/{id}/link"
    DIGITAL_FILE_RENAME = "/v1/digitalfiles/{id}/rename"
    DIGITAL_FILE_REINDEX = "/v1/digitalfiles/{id}/reindex"
    
    # Reel Endpoints
    REELS = "/v1/reels"
    REEL_BY_ID = "/v1/reels/{id}"
    REELS_BY_SHOW = "/v1/reels?show={show}"
    REELS_BATCH = "/v1/reels/batch"
    
    # Project Endpoints
    PROJECTS = "/v1/projects"
    PROJECT_BY_ID = "/v1/projects/{id}"
    PROJECTS_BY_LOCATION = "/v1/projects?location={location}"
    
    # SSL Certificate Endpoints
    SSL_CERTIFICATES = "/v1/sslcertificates"
    SSL_CERTIFICATE_BY_ID = "/v1/sslcertificates/{id}"
    
    # Dynamic Thumbnail Endpoints
    DYNAMIC_THUMBNAILS = "/dynamicthumbnails/{id}"
    
    # Feeder Endpoints
    FEEDERS = "/v1/feeders"
    FEEDER_BY_ID = "/v1/feeders/{id}"
    
    # Category Endpoints
    CATEGORIES = "/v1/categories"
    CATEGORY_BY_ID = "/v1/categories/{id}"
    CATEGORIES_BY_LOCATION = "/v1/categories?location={location}"
    
    # System Endpoints
    API_CREDENTIALS = "/v1/system/cablecastcloudservers/apicredentials"
    FORCE_CHECKIN = "/v1/system/cablecastcloudservers/forcecheckin"
    
    # Location Endpoints
    LOCATIONS = "/v1/locations"
    LOCATION_BY_ID = "/v1/locations/{id}"
    
    # Show Public Files
    SHOW_PUBLIC_FILES = "/shows/{id}/publicfiles/{showFieldPublicSiteId}"
    
    # Public Site Data Endpoints
    PUBLIC_SITE_DATA = "/publicsitedata"
    PUBLIC_SITE_SHOW = "/publicsitedata/shows/{showId}"
    PUBLIC_SITE_SHOWS = "/publicsitedata/shows"
    PUBLIC_SITE_SHOWS_SEARCH = "/publicsitedata/shows/search"
    PUBLIC_SITE_SCHEDULE = "/publicsitedata/schedule"
    PUBLIC_SITE_GALLERY = "/publicsitedata/galleries/{gallery_id}"
    
    # VOD Configuration Endpoints
    VOD_CONFIGURATIONS = "/v1/vodconfigurations"
    VOD_CONFIGURATION_BY_ID = "/v1/vodconfigurations/{id}"
    VOD_CONFIGURATIONS_BY_LOCATION = "/v1/vodconfigurations?location={location}&provider_name={provider_name}"
    
    # Log Endpoints
    LOGS = "/v1/logs"
    
    # Options Endpoints
    OPTIONS = "/v1/options"
    OPTION_BY_ID = "/v1/options/{id}"
    OPTIONS_BY_NAME = "/v1/options?name={name}"
    
    # Migration Status Endpoints
    MIGRATION_STATUS = "/v1/cablecastmigrationstatus"
    SET_MIGRATION_STATUS = "/v1/cablecastmigrationstatus?status={status}"
    MIGRATION_ENABLED = "/v1/cablecastmigrationenabled"
    
    # Channel Endpoints
    CHANNEL_BY_ID = "/v1/channels/{id}"
    CHANNELS_WITH_INCLUDE = "/v1/channels?include={include}"
    
    # Show Fields Endpoints
    SHOW_FIELDS = "/v1/showfields"
    SHOW_FIELD_BY_ID = "/v1/showfields/{id}"
    
    # Block Endpoints
    BLOCKS = "/v1/blocks"
    BLOCK_BY_ID = "/v1/blocks/{id}"
    
    # Block Parameters
    BLOCK_NAME = "name"
    BLOCK_OFFSETS = "offsets"
    BLOCK_LOCATION = "location"
    DEFAULT_SOURCE_TIME = "defaultSourceTime"
    
    # Automation Status Endpoints
    AUTOMATION_STATUS = "/v1/automationstatus"
    
    # Custom Fields Endpoints
    CUSTOM_FIELDS = "/v1/customfields"
    CUSTOM_FIELD_BY_ID = "/v1/customfields/{id}"
    CUSTOM_FIELDS_BY_LOCATION = "/v1/customfields?location_id={location_id}"
    
    # Force Events Endpoints
    FORCE_EVENTS = "/v1/forceevents"
    
    # System Assets Endpoints
    SYSTEM_ASSETS_UPLOAD = "/v1/systemassets/upload"
    
    # User Session Endpoints
    USER_SESSION = "/v1/usersession"
    
    # Release Invitation Endpoints
    RELEASE_INVITATIONS = "/v1/releaseinvitations"
    RELEASE_INVITATION_BY_ID = "/v1/releaseinvitations/{id}"
    
    # CCS Info Endpoints
    CCS_INFOS = "/v1/ccsinfos"
    
    # Event Summary Endpoints
    EVENT_SUMMARIES = "/v1/eventsummaries"
    
    # Live Stream Quality Endpoints
    LIVE_STREAM_QUALITIES = "/v1/livestreamqualities"
    LIVE_STREAM_QUALITY_BY_ID = "/v1/livestreamqualities/{id}"
    LIVE_STREAM_QUALITIES_BY_LOCATION = "/v1/livestreamqualities?location={location}"
    
    # Output Endpoints
    OUTPUTS = "/v1/outputs"
    OUTPUT_BY_ID = "/v1/outputs/{id}"
    OUTPUTS_BY_LOCATION = "/v1/outputs?location={location}"
    
    # Thumbnail Endpoints
    THUMBNAILS = "/v1/thumbnails/{slug}"
    
    # File Upload Endpoints
    FILE_UPLOADS = "/v1/fileuploads"
    FILE_UPLOAD_BY_ID = "/v1/fileuploads/{id}"
    FILE_UPLOAD_UPLOAD = "/v1/fileuploads/{id}/upload"
    
    # Manual Event Endpoints
    MANUAL_EVENTS = "/v1/manualevents"
    MANUAL_EVENT_BY_ID = "/v1/manualevents/{id}"
    MANUAL_EVENTS_BATCH = "/v1/manualevents/batch"
    MANUAL_EVENTS_FILTERED = "/v1/manualevents?start={start}&end={end}&channel={channel}"
    
    # License Endpoints
    LICENSES = "/v0/licenses"
    
    # Digital File Link Endpoints
    DIGITAL_FILE_LINKS = "/v1/digitalfilelinks"
    DIGITAL_FILE_LINK_BY_ID = "/v1/digitalfilelinks/{id}"
    DIGITAL_FILE_LINKS_BY_REEL = "/v1/digitalfilelinks?reelId={reelId}"
    
    # Chapter Endpoints
    CHAPTERS = "/v1/chapters"
    CHAPTER_BY_ID = "/v1/chapters/{id}"
    CHAPTERS_BY_VOD = "/v1/chapters?vod={vod}&deleted={deleted}"
    
    # Digital File Link Parameters
    LINK_TYPE = "linkType"
    REEL_ID = "reelId"
    
    # Chapter Parameters
    CHAPTER_TITLE = "title"
    CHAPTER_BODY = "body"
    OPERATOR_NOTE = "operatorNote"
    OFFSET = "offset"
    QUICK_ADDED = "quickAdded"
    ORDER = "order"
    DELETED = "deleted"
    HIDDEN = "hidden"
    
    # NDI Sources Endpoints
    NDI_SOURCES = "/v1/ndisources"
    
    # Site Gallery Endpoints
    SITE_GALLERIES = "/v1/sitegalleries"
    SITE_GALLERY_BY_ID = "/v1/sitegalleries/{id}"
    SITE_GALLERIES_BY_SITE = "/v1/sitegalleries?public_site={public_site}"
    
    # Site Gallery Parameters
    PUBLIC_SITE = "public_site"
    SAVED_SHOW_SEARCH = "savedShowSearch"
    DISPLAY_NAME = "displayName"
    DISPLAY_LIMIT = "displayLimit"
    POSITION = "position"
    
    # Public Site Search Endpoints
    PUBLIC_SITE_SEARCHES = "/v1/publicsitesearches"
    PUBLIC_SITE_SEARCH_BY_ID = "/v1/publicsitesearches/{id}"
    PUBLIC_SITE_SEARCHES_BY_SITE = "/v1/publicsitesearches?public_site={public_site}"
    
    # Crawl Event Endpoints
    CRAWL_EVENTS = "/v1/crawlevents"
    CRAWL_EVENT_BY_ID = "/v1/crawlevents/{id}"
    CRAWL_EVENTS_BATCH = "/v1/crawlevents/batch"
    CRAWL_EVENTS_FILTERED = "/v1/crawlevents?start={start}&end={end}&channel_id={channel_id}"
    
    # Show Endpoints
    SHOWS = "/v1/shows"
    SHOW_BY_ID = "/v1/shows/{id}"
    SHOWS_SEARCH = "/v1/shows/search/advanced"
    SHOWS_SEARCH_BY_ID = "/v1/shows/search/advanced/{id}"
    SHOWS_FILTERED = "/v1/shows?page_size={page_size}&offset={offset}&project={project}&location={location}"
    
    # First Run Endpoints
    FIRST_RUNS = "/v1/firstruns"
    FIRST_RUN_BY_ID = "/v1/firstruns/{id}"
    FIRST_RUNS_FILTERED = "/v1/firstruns?start={start}&end={end}&include={include}"
    
    # System Time Endpoints
    SYSTEM_TIME = "/v1/systemtime"
    
    # System Base Search Endpoints
    SYSTEM_BASE_SEARCHES = "/v1/systembasesearches"
    SYSTEM_BASE_SEARCH_BY_ID = "/v1/systembasesearches/{id}"
    
    # VOD Transcode Quality Endpoints
    VOD_TRANSCODE_QUALITIES = "/v1/vodtranscodequalities"
    VOD_TRANSCODE_QUALITY_BY_ID = "/v1/vodtranscodequalities/{id}"
    
    # RAID Info Endpoints
    RAID_INFOS = "/v1/raidinfos"
    RAID_INFO_BY_ID = "/v1/raidinfos/{id}"
    
    # Plugin Endpoints
    PLUGINS = "/v1/plugins"
    PLUGIN_BY_ID = "/v1/plugins/{id}"
    
    # Batch Show Action Endpoints
    BATCH_SHOW_ACTIONS = "/v1/batchshowactions"
    
    # Server Endpoints
    SERVERS = "/v1/servers"
    SERVER_BY_ID = "/v1/servers/{id}"
    SERVER_SUPPORTED_FEATURES = "/v1/servers/{id}/supportedfeatures"
    SERVER_CONFIGURATION = "/v1/servers/{id}/configuration"
    SERVER_CONNECTION = "/v1/servers/{id}/connection"
    
    # System Info Endpoints
    SYSTEM_INFO = "/v1/systeminfo"
    SYSTEM_INFO_UPDATE_DISMISS = "/v1/systeminfo/softwareupdate/dismiss"
    
    # Text Tracks Endpoints
    TEXT_TRACKS_EDIT_LOAD = "/v1/texttracks/edit/{id}/load"
    TEXT_TRACKS_EDIT_INTERMEDIATE = "/v1/texttracks/edit/{id}/intermediate"
    TEXT_TRACKS_EDIT_PUBLISH = "/v1/texttracks/edit/{id}/publish"
    
    # System Settings Endpoints
    SYSTEM_SETTINGS = "/v1/systemsettings"
    
    # Producer Endpoints
    PRODUCERS = "/v1/producers"
    PRODUCER_BY_ID = "/v1/producers/{id}"
    PRODUCERS_BY_LOCATION = "/v1/producers?location={location}"
    
    # Format Endpoints
    FORMATS = "/v1/formats"
    FORMAT_BY_ID = "/v1/formats/{id}"
    FORMATS_BY_LOCATION = "/v1/formats?location={location}"
    
    # Media Endpoints
    MEDIA = "/v1/media"
    MEDIA_BY_ID = "/v1/media/{id}"
    MEDIA_BATCH = "/v1/media/batch"
    
    # Format Parameters
    PRIMITIVE_FORMAT = "primitiveFormat"
    FORMAT_NAME = "name"
    FORMAT_LOCATION = "location"
    
    # Media Parameters
    CREATION_DATE = "creation_date"
    CREATION_DATE_OPERATOR = "creation_date_operator"
    DISPOSITION_DATE = "disposition_date"
    DISPOSITION_DATE_OPERATOR = "disposition_date_operator"
    DISPOSITION = "disposition"
    MEDIA_NAME = "media_name"
    PRE_ASSIGNED_DEVICE = "preAssignedDevice"
    PRE_ASSIGNED_DEVICE_SLOT = "preAssignedDeviceSlot"
    OVERRIDE_ASPECT_RATIO = "overrideAspectRatio"
    NETWORK_STREAM = "networkStream"
    
    # Schedule Item Parameters
    RUN_DATE_TIME = "runDateTime"
    RUN_BUMP = "runBump"
    RUN_LOCK = "runLock"
    RUN_TYPE = "runType"
    BUG_TEXT = "bugText"
    CRAWL_TEXT = "crawlText"
    CRAWL_LENGTH = "crawlLength"
    CG_EXEMPT = "cgExempt"
    ID_TYPE = "idType"
    MANUAL_EVENT = "manualEvent"
    RUN_STATUS = "runStatus"
    RECORD_EVENTS = "recordEvents"
    FILLER = "filler"
    SCHEDULE_RULE = "scheduleRule"
    
    # Schedule Gap Parameters
    FILLER_SEARCH = "fillerSearch"
    OPEN_SEARCH = "openSearch"
    CLOSE_SEARCH = "closeSearch"
    PRE_FILL_SEARCH = "preFillSearch"
    POST_FILL_SEARCH = "postFillSearch"
    FILL_MODE = "fillMode"
    MAXIMUM_BUMP = "maximumBump"
    
    # Event Endpoints
    EVENTS = "/v1/events"
    EVENT_BY_ID = "/v1/events/{id}"
    EVENTS_BY_LOCATION = "/v1/events?location={location}&channel={channel}"
    
    # User Settings Endpoints
    USER_SETTINGS = "/v1/usersettings/{name}"
    
    # System Archives Endpoints
    SYSTEM_ARCHIVES = "/v1/systemarchives"

class CablecastParameters:
    """Common Cablecast API Parameters"""
    
    # Pagination Parameters
    PAGE_SIZE = "page_size"
    OFFSET = "offset"
    
    # Filter Parameters
    LOCATION = "location"
    CHANNEL = "channel"
    INCLUDE = "include"
    QUERY = "query"
    SORT = "sort"
    SORT_ORDER = "sort_order"
    
    # Time Range Parameters
    START = "start"
    END = "end"
    SINCE = "since"
    
    # Chaptering Session Parameters
    VOD_ID = "vod"
    SCHEDULE_ITEM_ID = "scheduleItem"
    SESSION_ENDED = "sessionEnded"
    START_TIME = "startTime"
    
    # IFrame Parameters
    IFRAME_LOCATION = "location"
    IFRAME_URL = "url"
    IFRAME_TITLE = "title"
    IFRAME_HEIGHT = "height"
    
    # Device Parameters
    DEVICE_LOCATION = "location"
    DEVICE_TYPE = "deviceType"
    DEVICE_ADDRESS = "deviceAddress"
    DEVICE_NAME = "name"
    DEVICE_STATUS = "deviceStatus"
    DEVICE_FORMAT = "format"
    
    # ShowFile Parameters
    SHOW_ID = "show_id"
    FILE_ID = "file"
    ASSET_ID = "asset"
    
    # AssetLog Parameters
    ASSET_ID = "asset_id"
    WORKFLOW_ID = "workflowId"
    MESSAGE_TYPE = "messageType"
    SOURCE_STORE = "sourceStore"
    DESTINATION_STORE = "destinationStore"
    
    # Network Stream Parameters
    STREAM_TYPE = "streamType"
    CAPTIONS_ENABLED = "captionsEnabled"
    CAPTION_VOCABULARY = "captionVocabulary"
    TRANSLATIONS_ENABLED = "translationsEnabled"
    TRANSLATION_LANGUAGE = "translationLanguage"
    STANDBY_GRAPHIC = "standbyGraphic"
    
    # VOD Transaction Parameters
    TRANSACTION_TYPE = "transactionType"
    PERCENT_COMPLETE = "percentComplete"
    
    # Volume Info Parameters
    DRIVE_LETTER = "driveLetter"
    CAPACITY = "capacity"
    FREE_SPACE = "free"
    SERVER_ID = "server"
    
    # Record Event Parameters
    RUN_DATE_TIME = "runDateTime"
    PLAY_DEVICE = "playDevice"
    RECORD_DEVICE = "recordDevice"
    RUN_STATUS = "runStatus"
    
    # Digital File Parameters
    FILE_NAME = "fileName"
    FILE_SIZE = "fileSize"
    FRAME_COUNT = "frameCount"
    FRAME_RATE = "frameRate"
    CODEC = "codec"
    ASPECT_RATIO = "aspectRatio"
    IS_VALID = "isValid"
    IS_STREAMABLE = "isStreamable"
    
    # Reel Parameters
    REEL_NUMBER = "reelNumber"
    USER_FILE_NAME = "userFileName"
    PLAYBACK_ASSET = "playbackAsset"
    HAS_VALID_FILE = "hasValidFile"
    
    # Project Parameters
    PROJECT_NAME = "name"
    PROJECT_DESCRIPTION = "description"
    PROJECT_PRODUCER = "producer"
    PROJECT_PODCAST = "podcast"
    PODCAST_NAME = "podcastName"
    PODCAST_DESCRIPTION = "podcastDescription"
    PODCAST_URL = "podcastUrl"
    
    # SSL Certificate Parameters
    DOMAIN_NAME = "domainName"
    EMAIL_ADDRESS = "emailAddress"
    PRIMARY_CERTIFICATE = "primaryCertificate"
    HTTP_PORT = "httpPort"
    IS_ACTIVE = "isActive"
    IS_LETS_ENCRYPT = "isLetsEncrypt"
    
    # Dynamic Thumbnail Parameters
    DIMENSIONS = "d"
    FIT_MODE = "fit_mode"
    
    # Feeder Parameters
    FEEDER_LOCATION = "feederLocation"
    FEEDER_OUTPUT = "feederOutput"
    PRIMARY_INPUT = "primaryInput"
    
    # Category Parameters
    CATEGORY_NAME = "name"
    CATEGORY_LOCATION = "location"
    
    # Location Parameters
    LOCATION_NAME = "name"
    VOD_CONFIGURATIONS = "vodConfigurations"
    ROUTER_CONTROL_MODULE_SET = "routerControlModuleSet"
    
    # Control Module Parameters
    CONTROL_MODULE = "controlModule"
    PORT_SETTING = "portSetting"
    SERVER = "server"
    
    # Public Site Parameters
    SITE_ID = "site"
    SHOW_ID = "showId"
    GALLERY_ID = "gallery_id"
    CURRENT_DAY = "current_day"
    SEARCH = "search"
    
    # VOD Configuration Parameters
    PROVIDER_NAME = "provider_name"
    DEFAULT_QUALITY = "defaultQuality"
    EMBED_TEMPLATE = "embedTemplate"
    VOD_CONTROL_MODULE_SET = "vodControlModuleSet"
    VOD_TRANSCODE_QUALITIES = "vodTranscodeQualities"
    MAXIMUM_RESOLUTION = "maximumResolution"
    
    # Log Parameters
    MACHINE_NAME = "machineName"
    LOGGED = "logged"
    LEVEL = "level"
    MESSAGE = "message"
    LOGGER = "logger"
    EXCEPTION = "exception"
    
    # Options Parameters
    OPTION_NAME = "name"
    OPTION_VALUE = "value"
    
    # Migration Parameters
    MIGRATION_STATUS = "status"
    MIGRATION_ENABLED = "enabled"
    
    # Channel Parameters
    PRIMARY_LOCATION = "primaryLocation"
    PRIMARY_OUTPUT = "primaryOutput"
    INTERSTITIAL_DWELL = "interstitialDwell"
    LIVE_STREAMS = "liveStreams"
    CHANNEL_CONTACT_INFO = "channelContactInfo"
    AUTOMATION_OVERRIDEN = "automationOverriden"
    BRANDING_CONFIG = "brandingConfig"
    SQUEEZE_BACK_ENABLED = "squeezeBackEnabled"
    SQUEEZE_BACK_CHANNEL = "squeezeBackChannel"
    SQUEEZE_BACK_BLOCK = "squeezeBackBlock"
    
    # Show Field Parameters
    FIELD_LABEL = "label"
    FIELD_DEFINITION = "fieldDefinition"
    MAX_INSTANCES = "maxInstances"
    FIELD_TYPE = "type"
    FIELD_WIDGET = "widget"
    FIELD_LOCATION = "location"
    FIELD_OPTION = "option"
    FIELD_POSITION = "position"
    
    # Automation Status Parameters
    EXCLUDE = "exclude"
    
    # Custom Fields Parameters
    LOCATION_ID = "location_id"
    CUSTOM_FIELD_NUMBER = "customFieldNumber"
    FIELD_NAME = "fieldName"
    FIELD_TYPE = "fieldType"
    
    # System Assets Parameters
    FILE_TYPE = "file_type"
    
    # Live Stream Parameters
    PUBLIC_BASE_URL = "publicBaseUrl"
    REFLECT_BASE_URL = "reflectBaseUrl"
    CABLECAST_BASE_URL = "cablecastBaseUrl"
    VIDEO_INPUT = "videoInput"
    AUDIO_INPUT = "audioInput"
    QUALITIES = "qualities"
    EMBED_TEMPLATE = "embedTemplate"
    INPUT_RESOLUTION = "inputResolution"
    REFLECT_ENABLED = "reflectEnabled"
    IP_EXEMPT_PAUSED_TEMPLATE = "ipExemptPausedTemplate"
    STOPPED_TEMPLATE = "stoppedTemplate"
    AUTO_PLAY = "autoPlay"
    POSTER = "poster"
    NEW_STATE = "newState"
    
    # Event Summary Parameters
    SINCE = "since"
    FUTURE = "future"
    LIMIT_PER_CHANNEL = "limit_per_channel"
    
    # Live Stream Quality Parameters
    SETTINGS_HASH = "settingsHash"
    DESCRIPTION_TEMPLATE = "descriptionTemplate"
    
    # Output Parameters
    OUTPUT_TYPE = "outputType"
    OUTPUT_NUMBER = "outputNumber"
    DEFAULT_INPUT = "defaultInput"
    FADE_CMS = "fadeCms"
    RATING_CMS = "ratingCms"
    PRIMARY_DEVICE = "primaryDevice"
    USE_CABLECAST_CG = "useCablecastCgAsDefaultSource"
    OUTPUT_PATCH = "outputPatch"
    LBAR_ENABLED = "lBarEnabled"
    LBAR_BLOCK = "lBarBlock"
    
    # Thumbnail Parameters
    SLUG = "slug"
    WIDTH = "width"
    HEIGHT = "height"
    FORMAT = "format"
    
    # File Upload Parameters
    FILE_NAME = "fileName"
    DESTINATION_STORE = "destinationStore"
    TOTAL_SEGMENTS = "totalSegments"
    FILE_STATE = "state"
    FILE_SIZE = "size"
    
    # Manual Event Parameters
    EVENT_NAME = "name"
    EVENT_LENGTH = "length"
    DEVICE = "device"
    DEVICE_ACTION = "deviceAction"
    DEVICE_SLOT = "deviceSlot"
    DEVICE_TITLE = "deviceTitle"
    DEVICE_CHAPTER = "deviceChapter"
    DEVICE_CUE = "deviceCue"
    DEVICE_FILE_KEY = "deviceFileKey"
    CHANNEL = "channel"
    START = "start"
    END = "end"
    
    # Public Site Search Parameters
    SAVED_SHOW_SEARCH = "savedShowSearch"
    SEARCH_LIMIT = "searchLimit"
    POSITION = "position"
    
    # Crawl Event Parameters
    CHANNEL_ID = "channel_id"
    EVENT_START = "start"
    EVENT_LENGTH = "length"
    EVENT_TEXT = "text"
    EVENT_DELETED = "deleted"
    PAGE_SIZE = "page_size"
    OFFSET = "offset"
    SINCE = "since"
    
    # Show Parameters
    PAGE_SIZE = "page_size"
    OFFSET = "offset"
    PROJECT = "project"
    LOCATION = "location"
    SEARCH = "search"
    FREE = "free"
    SORT_ORDER = "sort_order"
    INCLUDE = "include"
    IDS = "ids"
    SINCE = "since"
    
    # Show Search Parameters
    SEARCH_NAME = "name"
    SEARCH_QUERY = "query"
    SEARCH_RESULTS = "results"
    SEARCH_FIELD = "field"
    SEARCH_OPERATOR = "operator"
    SEARCH_VALUE = "searchValue"
    SEARCH_OR_AND = "orAnd"
    SEARCH_DESCENDING = "descending"
    
    # System Time Parameters
    CLIENT_TIME = "client_time"
    TIME_ZONE = "timeZone"
    GMT_OFFSET = "gmtOffset"
    CLIENT_OFFSET = "clientOffset"
    IANA_TIME_ZONE = "ianaTimeZone"
    
    # System Base Search Parameters
    SAVED_SHOW_SEARCH = "savedShowSearch"
    SEARCH_LIMIT = "searchLimit"
    POSITION = "position"
    
    # VOD Transcode Quality Parameters
    VOD_PROVIDER = "vodProvider"
    SETTINGS_HASH = "settingsHash"
    DESCRIPTION_TEMPLATE = "descriptionTemplate"
    
    # RAID Info Parameters
    RAID_TYPE = "type"
    RAID_STATUS = "status"
    LAST_MODIFIED = "lastModified"
    
    # Batch Show Action Parameters
    ACTION_TYPE = "type"
    SHOWS = "shows"
    
    # Server Parameters
    HOST_ADDRESS = "hostAddress"
    TIME_DELTA = "timeDelta"
    REMOTE_ACCESS_ID = "remoteAccessId"
    AUDIO_DEVICE = "audioDevice"
    VOLUME_ADJUSTMENT = "volumeAdjustment"
    SERVER_MODEL = "serverModel"
    IS_VIDEO_SERVER = "isVideoServer"
    
    # Server Configuration Parameters
    SERVER_ID = "serverId"
    LOCATION_ID = "locationId"
    MODE = "mode"
    AUDIO_NORM_ENABLED = "audioNormEnabled"
    ADDITIONAL_FILE_STORES = "additionalFileStores"
    ROUTER_OUTPUT_ADDRESS = "routerOutputAddress"
    CHANNEL_IDS = "channelIds"
    CHANNEL_ROUTER_OUTPUT_ADDRESS = "channelRouterOutputAddress"
    ROUTER_INPUT_ADDRESS = "routerInputAddress"
    USE_CG_AS_DEFAULT_INPUT = "useCgAsDefaultInput"
    RESOLUTION = "resolution"
    
    # System Info Parameters
    HARDWARE_ID = "hardwareID"
    CABLECAST_VERSION = "cablecastVersion"
    SITE_NAME = "siteName"
    BASE_URL_FOR_EMBEDS = "baseUrlForEmbeds"
    
    # Caption Editor Parameters
    MEDIA_URL = "mediaUrl"
    THUMBNAIL_URL = "thumbnailUrl"
    MEDIA_TYPE = "mediaType"
    ASPECT_RATIO = "aspectRatio"
    CAPTION_TYPE = "captionType"
    PUBLISH_ENDPOINT = "publishEndpoint"
    PROJECT_NAME = "projectName"
    FRAME_RATE = "frameRate"
    DROP_FRAME = "dropFrame"
    
    # System Settings Parameters
    AUTO_DATABASE_BACKUP_OPT_OUT = "autoDatabaseBackupOptOut"
    
    # Producer Parameters
    PRODUCER_ACTIVE = "active"
    PRODUCER_ADDRESS = "address"
    PRODUCER_CONTACT = "contact"
    PRODUCER_EMAIL = "email"
    PRODUCER_NOTES = "notes"
    PRODUCER_PHONE_ONE = "phoneOne"
    PRODUCER_PHONE_TWO = "phoneTwo"
    PRODUCER_NAME = "name"
    PRODUCER_WEBSITE = "website"
    
    # Event Parameters
    CONTROL_MODULE_SET = "controlModuleSet"
    ROUTER_CONTROL_MODULE_SET = "routerControlModuleSet"
    ROUTER_ACTION = "routerAction"
    DEVICE_CONTROL_MODULE_SET = "deviceControlModuleSet"
    DEVICE_ACTION = "deviceAction"
    DEVICE_RECORD_QUALITY = "deviceRecordQuality"
    CG_CODE = "cgCode"
    AUTOPILOT_SEND = "autopilotSend"
    
    # User Settings Parameters
    DISPLAY_24_HOUR_TIME = "displayTwentyFourHourTime"
    DEFAULT_LOCATION = "defaultLocation"
    DEFAULT_CHANNEL = "defaultChannel"
    DEVICE_ASSIGNMENTS_MODE = "deviceAssignmentsMode"

class CablecastStreamStates(Enum):
    """Live Stream States"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class CablecastVODStates(Enum):
    """VOD Processing States"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    DELETED = "deleted"

class ChapteringSessionStates(Enum):
    """Chaptering Session States"""
    ACTIVE = "active"
    ENDED = "ended"

class CablecastErrorTypes:
    """Common Error Types"""
    AUTHENTICATION_ERROR = "AuthenticationError"
    PERMISSION_ERROR = "PermissionError"
    NOT_FOUND_ERROR = "NotFoundError"
    VALIDATION_ERROR = "ValidationError"
    STREAM_ERROR = "StreamError"
    VOD_ERROR = "VODError"
    DEVICE_ERROR = "DeviceError" 

class DeviceTypes(Enum):
    """Device Types"""
    LIVE = "live"
    ROUTER = "router"
    ENCODER = "encoder"
    DECODER = "decoder"
    PLAYER = "player"
    RECORDER = "recorder"

class DeviceStates(Enum):
    """Device States"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    BUSY = "busy"
    IDLE = "idle"

class AssetLogMessageTypes(Enum):
    """Asset Log Message Types"""
    DISCOVERED = "discovered"
    DELETED = "deleted"
    TRANSFERRED = "transferred"
    ERROR = "error"
    PROCESSING = "processing"

class PublicSiteParameters:
    """Public Site Parameters"""
    SITE_NAME = "siteName"
    LOGO = "logo"
    INCLUDE_IN_INDEX = "includeInIndex"
    GALLERY_TITLE = "galleryTitle"
    GALLERY_SAVED_SEARCH = "gallerySavedSearch"
    CAROUSEL_SAVED_SEARCH = "carouselSavedSearch"
    ABOUT_PAGE_DESCRIPTION = "aboutPageDescription"
    ABOUT_PAGE_SHORT_DESCRIPTION = "aboutPageShortDescription"
    CUSTOM_COLORS = ["customColor1", "customColor2", "customColor3", "customColor4"]
    SOCIAL_URLS = ["twitterUrl", "facebookUrl", "blogUrl"]
    CONTACT_INFO = ["contactPhone", "contactEmail"]
    SQUARE_LOGO = "squareLogo"
    GOOGLE_ANALYTICS_ID = "googleAnalyticsId"
    CHANNEL = "channel"

class ChannelBrandingParameters:
    """Channel Branding Parameters"""
    CHANNEL_ID = "channelID"
    BUG_TEXT = "bugText"
    BUG_STATE = "bugState"
    DEVICE_ADDRESS = "deviceAddress"
    DEVICE_ID = "deviceID"
    SQUEEZED_BACK_STATE = "squeezedBackState"
    CRAWL_TEXT = "crawlText"
    CRAWL_SPEED = "crawlSpeed"
    CMS_ID = "cmsid"
    EXPIRES_TIME = "expiresTime"
    START_TIME = "startTime"