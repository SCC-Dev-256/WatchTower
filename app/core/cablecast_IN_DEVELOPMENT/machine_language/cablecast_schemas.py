from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ServerUpdateStatus(BaseModel):
    """Server Update Status Model"""
    server: int
    serverName: str
    serverVersion: str
    connectionState: str = "ok"
    lastSeen: datetime
    serverJobStatus: str = "pending"

class SystemInfo(BaseModel):
    """System Info Model"""
    hardwareID: str
    cablecastVersion: str
    cablecastFriendlyVersion: str
    siteName: str
    databaseBackupsConfigured: bool
    softwareMetricsConfigured: bool
    updatesAvailable: bool
    baseUrlForEmbeds: str
    updateInProgress: bool
    serverUpdateStatuses: List[ServerUpdateStatus]
    activeReleaseStatus: int
    timestamp: datetime

class Show(BaseModel):
    """Show Model"""
    id: int
    title: str
    location: int
    project: Optional[int]
    producer: Optional[int]
    category: Optional[int]
    comments: Optional[str]
    customFields: Optional[Dict]
    lastModified: datetime
    eventDate: datetime
    duration: int

class Asset(BaseModel):
    """Asset Model"""
    id: int
    name: str
    path: str
    type: str
    size: int
    created: datetime
    modified: datetime
    metadata: Optional[Dict]

class FieldDisplay(BaseModel):
    """Field Display Configuration"""
    id: int
    name: str
    enabled: bool
    order: int
    displayType: str

class ShowBase(BaseModel):
    """Base Show Model"""
    id: int
    title: str
    event_date: datetime
    duration: int
    project_id: Optional[int]
    producer_id: Optional[int]
    category_id: Optional[int]
    comments: Optional[str]
    custom_fields: Optional[Dict]

class ScheduleItem(BaseModel):
    """Schedule Item Model"""
    id: int
    channel: int
    show: int
    runDateTime: datetime
    runBump: int
    runLock: bool
    runType: int
    bugText: str
    crawlText: str
    crawlLength: int
    cgExempt: bool
    idType: int
    manualEvent: int
    runStatus: int
    deleted: bool
    recordEvents: List[int]
    filler: bool
    scheduleRule: int
    liveCaptions: bool
    encoder: int
    captionProvider: str
    captionVocabulary: int
    liveTranslations: bool
    sourceLanguage: str
    translationLanguage: str
    hasFiles: bool
    hasValidFile: bool
    hasInvalidFile: bool
    hasProcessingFile: bool

class ScheduleItemResource(BaseModel):
    """Single ScheduleItem Resource Response"""
    scheduleItem: ScheduleItem

class ScheduleItemsResource(BaseModel):
    """ScheduleItems Collection Response"""
    meta: Dict[str, int]
    scheduleItems: List[ScheduleItem]

class LiveStreamConfig(BaseModel):
    """Live Stream Configuration"""
    id: int
    name: str
    url: str
    quality_id: int
    enabled: bool
    state: str
    server_id: Optional[int]
    device_id: Optional[int]

class VODStatus(BaseModel):
    """VOD Status Model"""
    id: int
    show_id: int
    state: str
    progress: Optional[float]
    duration: Optional[int]
    file_size: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    chapters_published: bool = False

class DeviceStatus(BaseModel):
    """Device Status Model"""
    id: int
    name: str
    type: str
    state: str
    connection_status: str
    last_communication: datetime
    errors: Optional[List[str]]
    warnings: Optional[List[str]]
    ip_address: Optional[str]
    version: Optional[str]

class PublicSite(BaseModel):
    """Public Site Configuration"""
    id: int
    siteName: str
    logo: int
    includeInIndex: bool
    galleryTitle: str
    gallerySavedSearch: int
    siteGalleries: List[int]
    publicSiteSearches: List[int]
    fieldDisplays: List[FieldDisplay]
    carouselSavedSearch: int
    aboutPageDescription: str
    aboutPageShortDescription: str
    customColor1: str
    customColor2: str
    customColor3: str
    customColor4: str
    twitterUrl: Optional[str]
    facebookUrl: Optional[str]
    blogUrl: Optional[str]
    contactPhone: Optional[str]
    contactEmail: Optional[str]
    squareLogo: int
    googleAnalyticsId: Optional[str]
    channel: int

class PublicSiteResource(BaseModel):
    """Single PublicSite Resource Response"""
    publicSite: PublicSite

class PublicSitesResource(BaseModel):
    """PublicSites Collection Response"""
    publicSites: List[PublicSite]

class PublicSiteResponse(BaseModel):
    """PublicSite HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class ServerConfig(BaseModel):
    """Server Configuration"""
    id: int
    name: str
    type: str
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    enabled: bool
    features: List[str]
    status: str 

class ChapteringSession(BaseModel):
    """Chaptering Session Model"""
    id: int
    vod: int
    scheduleItem: int
    startTime: datetime
    sessionEnded: bool

class ChapteringSessionResource(BaseModel):
    """Chaptering Session Resource Response"""
    chapteringSession: ChapteringSession

class ChapteringSessionsResource(BaseModel):
    """Chaptering Sessions Collection Response"""
    chapteringSessions: List[ChapteringSession]

class ChapteringSessionResponse(BaseModel):
    """Chaptering Session HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]

class IFrame(BaseModel):
    """IFrame Model"""
    id: int
    location: int
    url: str
    title: str
    height: int

class IFrameResource(BaseModel):
    """Single IFrame Resource Response"""
    iFrame: IFrame

class IFramesResource(BaseModel):
    """IFrames Collection Response"""
    iFrames: List[IFrame]

class Device(BaseModel):
    """Device Model"""
    id: int
    location: int
    name: str
    inputAddress: Optional[int]
    takeDelay: Optional[int]
    active: bool
    deviceType: int
    format1: Optional[int]
    format2: Optional[int]
    format3: Optional[int]
    controlModuleSet: Optional[int]
    endAction: Optional[int]
    runCount: Optional[int]
    postDelay: Optional[int]
    deviceAddress: Optional[str]
    deviceSlotStart: Optional[int]
    deviceSlotEnd: Optional[int]
    primitiveDevice: Optional[int]
    loadDuration: Optional[int]
    jumpDuration: Optional[int]
    recordQuality: Optional[int]
    outputAddress: Optional[int]
    recordCopyUnc: Optional[str]
    wakeDuration: Optional[int]
    wakeAction: Optional[int]
    allowedActions: Optional[List[str]]
    resolution: Optional[int]
    volumeAdjustment: Optional[float]
    normalizationEnabled: Optional[bool]
    targetLoudness: Optional[int]
    ndiEnabled: Optional[bool]
    deviceStatus: Optional[int]
    passthroughStatus: Optional[int]
    supportsPassthrough: Optional[bool]
    supportsNetworkStream: Optional[bool]
    standaloneCablecastCg: Optional[bool]
    encodeBitrate: Optional[int]
    encodeCodec: Optional[int]
    vioStream: Optional[bool]
    primaryEncodeLanguage: Optional[int]
    secondaryEncodeLanguage: Optional[int]

class DevicesResource(BaseModel):
    """Devices Collection Response"""
    devices: List[Device]

class DeviceStatusResource(BaseModel):
    """Device Status Response"""
    deviceStatus: DeviceStatus

class DeviceThumbnailsResource(BaseModel):
    """Device Thumbnails Response"""
    thumbnails: List[str]

class ShowFile(BaseModel):
    """ShowFile Model"""
    id: int
    show: int
    file: int
    asset: int

class ShowFileResource(BaseModel):
    """Single ShowFile Resource Response"""
    showFile: ShowFile

class ShowFilesResource(BaseModel):
    """ShowFiles Collection Response"""
    showFiles: List[ShowFile]

class ShowFileResponse(BaseModel):
    """ShowFile HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class AssetLog(BaseModel):
    """Asset Log Model"""
    id: int
    timeStamp: datetime
    asset: int
    messageType: str
    sourceDeleted: bool
    sourceStore: int
    destinationDeleted: bool
    destinationStore: int
    workflow: int

class AssetLogResource(BaseModel):
    """Single AssetLog Resource Response"""
    assetLog: AssetLog

class AssetLogsResource(BaseModel):
    """AssetLogs Collection Response with Meta"""
    meta: Dict[str, int]
    assetLogs: List[AssetLog]

class AssetLogResponse(BaseModel):
    """AssetLog HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class ChannelBrandingAssets(BaseModel):
    """Channel Branding Assets Model"""
    bugUrl: str
    bugTextUrl: str
    crawlBGUrl: str
    crawlFGUrl: str
    crawlTextUrl: str

class ChannelBrandingInfo(BaseModel):
    """Channel Branding Information Model"""
    channelID: int
    bugText: str
    deviceAddress: str
    deviceID: int
    bugState: bool
    squeezedBackState: bool
    crawlText: str
    crawlSpeed: float
    cmsid: int
    expiresTime: datetime
    startTime: datetime
    assets: ChannelBrandingAssets
    channelModified: datetime

class ChannelBrandingResponse(BaseModel):
    """Channel Branding Collection Response"""
    channelBranding: List[ChannelBrandingInfo]

    class Config:
        """Pydantic model configuration"""
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VodTransaction(BaseModel):
    """VOD Transaction Model"""
    id: int
    lastModified: datetime
    percentComplete: float
    startTime: datetime
    transactionType: int
    vod: int

class VodTransactionResource(BaseModel):
    """Single VodTransaction Resource Response"""
    vodTransaction: VodTransaction

class VodTransactionsResource(BaseModel):
    """VodTransactions Collection Response"""
    vodTransactions: List[VodTransaction]

class VodTransactionResponse(BaseModel):
    """VodTransaction HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class VolumeInfo(BaseModel):
    """Volume Information Model"""
    id: int
    driveLetter: str
    capacity: int  # Storage capacity
    free: int     # Free space
    server: int   # Server ID

class VolumeInfoResource(BaseModel):
    """Single VolumeInfo Resource Response"""
    volumeInfo: VolumeInfo

class VolumeInfosResource(BaseModel):
    """VolumeInfos Collection Response"""
    volumeInfos: List[VolumeInfo]

class VolumeStatsResponse(BaseModel):
    """Volume Statistics Response"""
    total_capacity: int
    total_free: int
    percent_used: float
    servers: Dict[int, Dict[str, int]]

class RecordEvent(BaseModel):
    """Record Event Model"""
    id: int
    location: int
    name: str
    runDateTime: datetime
    length: int
    media: int
    playDevice: int
    playDeviceSlot: int
    playDeviceTitle: int
    playDeviceChapter: int
    playDeviceCue: int
    playDeviceFileKey: str
    recordDevice: int
    recordDeviceSlot: int
    recordDeviceTitle: int
    recordDeviceChapter: int
    recordDeviceCue: int
    recordDeviceFileKey: str
    scheduleItem: int
    runStatus: int
    deleted: bool
    networkStream: int
    liveCaptions: bool
    captionProvider: str
    captionVocabulary: int
    liveTranslations: bool
    sourceLanguage: str
    translationLanguage: str

class RecordEventResource(BaseModel):
    """Single RecordEvent Resource Response"""
    recordEvent: RecordEvent

class RecordEventsResource(BaseModel):
    """RecordEvents Collection Response"""
    recordEvents: List[RecordEvent]

class RecordEventResponse(BaseModel):
    """RecordEvent HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class Disposition(BaseModel):
    """Disposition Model"""
    id: int
    location: int
    name: str
    allowAssignment: bool

class DispositionResource(BaseModel):
    """Single Disposition Resource Response"""
    disposition: Disposition

class DispositionsResource(BaseModel):
    """Dispositions Collection Response"""
    dispositions: List[Disposition]

class DispositionResponse(BaseModel):
    """Disposition HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class DigitalFile(BaseModel):
    """Digital File Model"""
    id: int
    ambiguous: bool
    aspectRatio: int
    bitrate: int
    server: int
    controlModuleSet: int
    codec: str
    created: datetime
    fileName: str
    fileSize: int
    frameCount: int
    frameRate: float
    height: int
    isValid: bool
    isDeprecated: bool
    location: int
    modified: datetime
    partial: bool
    path: str
    problemDescription: str
    reelNumber: int
    sampleRate: int
    show: int
    supportedFields: int
    updatedDateTime: datetime
    vbiExists: bool
    width: int
    reel: int
    thumbnails: List[int]
    mediaInfo: Optional[Dict]
    hasCaptions: bool
    captionsAreCompatible: bool
    captionsMessage: Optional[str]
    sha1: Optional[str]
    isStreamable: bool
    digitalFileLinks: Optional[List[int]]

class DigitalFileResource(BaseModel):
    """Single DigitalFile Resource Response"""
    digitalFile: DigitalFile

class DigitalFilesResource(BaseModel):
    """DigitalFiles Collection Response"""
    meta: Dict[str, int]
    digitalFiles: List[DigitalFile]

class DigitalFileRenameRequest(BaseModel):
    """Digital File Rename Request"""
    oldName: str
    newName: str

class DigitalFileResponse(BaseModel):
    """Digital File HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class Reel(BaseModel):
    """Reel Model"""
    id: int
    media: int
    chapter: int
    title: int
    length: int
    cue: int
    reelNumber: int
    show: int
    userFileName: str
    assetReelLinks: List[int]
    hasValidFile: bool
    hasInvalidFile: bool
    hasProcessingFile: bool
    playbackAsset: int

class ReelResource(BaseModel):
    """Single Reel Resource Response"""
    reel: Reel

class ReelsResource(BaseModel):
    """Reels Collection Response"""
    reels: List[Reel]

class ReelResponse(BaseModel):
    """Reel HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class NetworkStream(BaseModel):
    """Network Stream Model"""
    id: int
    name: str
    location: int
    address: str
    test: str
    deleted: bool
    streamType: str = "unknown"
    lastModified: datetime
    standbyGraphic: int
    captionsEnabled: bool
    captionVocabulary: int
    translationsEnabled: bool
    translationLanguage: str

class NetworkStreamResource(BaseModel):
    """Single NetworkStream Resource Response"""
    networkStream: NetworkStream
    assets: List[Asset]

class NetworkStreamsResource(BaseModel):
    """NetworkStreams Collection Response"""
    networkStreams: List[NetworkStream]
    assets: List[Asset]

class NetworkStreamResponse(BaseModel):
    """NetworkStream HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class Project(BaseModel):
    """Project Model"""
    id: int
    location: int
    name: str
    description: str
    producer: int
    podcast: bool
    podcastName: str
    podcastDescription: str
    podcastUrl: str

class ProjectResource(BaseModel):
    """Single Project Resource Response"""
    project: Project

class ProjectsResource(BaseModel):
    """Projects Collection Response"""
    projects: List[Project]

class ProjectResponse(BaseModel):
    """Project HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class SslCertificate(BaseModel):
    """SSL Certificate Model"""
    id: int
    errorMessage: Optional[str]
    state: int
    domainName: str
    emailAddress: str
    created: datetime
    lastChecked: datetime
    primaryCertificate: bool
    httpPort: int
    isActive: bool
    isLetsEncrypt: bool

class SslCertificateResource(BaseModel):
    """Single SSL Certificate Resource Response"""
    sslCertificate: SslCertificate

class SslCertificatesResource(BaseModel):
    """SSL Certificates Collection Response"""
    sslCertificates: List[SslCertificate]

class SslCertificateResponse(BaseModel):
    """SSL Certificate HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class DynamicThumbnail(BaseModel):
    """Dynamic Thumbnail Model"""
    id: int
    dimensions: str
    fit_mode: str = "preserve"

class DynamicThumbnailResponse(BaseModel):
    """Dynamic Thumbnail HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[bytes]

class Feeder(BaseModel):
    """Feeder Model"""
    id: int
    channel: int
    feederLocation: int
    feederOutput: int
    primaryInput: int

class FeederResource(BaseModel):
    """Single Feeder Resource Response"""
    feeder: Feeder

class FeedersResource(BaseModel):
    """Feeders Collection Response"""
    feeders: List[Feeder]

class Category(BaseModel):
    """Category Model"""
    id: int
    location: int
    name: str

class CategoryResource(BaseModel):
    """Single Category Resource Response"""
    category: Category

class CategoriesResource(BaseModel):
    """Categories Collection Response"""
    categories: List[Category]

class CategoryResponse(BaseModel):
    """Category HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class ApiCredentials(BaseModel):
    """API Credentials Model"""
    apiKeyId: str
    apiKeySecret: str

class ApiCredentialsResource(BaseModel):
    """API Credentials Resource"""
    apiCredentials: ApiCredentials

class Location(BaseModel):
    """Location Model"""
    id: int
    name: str
    vodConfigurations: List[int]
    routerControlModuleSet: int

class ControlModuleSet(BaseModel):
    """Control Module Set Model"""
    id: int
    server: int
    name: str
    controlModule: str
    location: int
    portSetting: str

class LocationResource(BaseModel):
    """Single Location Resource Response"""
    location: Location
    controlModuleSet: ControlModuleSet

class LocationsResource(BaseModel):
    """Locations Collection Response"""
    locations: List[Location]
    controlModuleSets: List[ControlModuleSet]

class PublicSiteConfig(BaseModel):
    """Public Site Configuration Model"""
    SiteId: int
    Title: str
    Logo: str
    SquareLogo: str
    PageDescription: str
    PageShortDescription: str
    SiteColorsCssLink: str
    PhoneNumber: str
    Email: str
    TwitterUrl: Optional[str]
    FacebookUrl: Optional[str]
    BlogUrl: Optional[str]
    GoogleAnalyticsId: Optional[str]
    LiveEmbedCode: str
    IncludeInIndex: bool
    HasPodcasts: bool
    UseFullTextIndex: bool
    SlideShow: List['PublicSiteShow']
    Galleries: List[int]

class VodChapter(BaseModel):
    """VOD Chapter Model"""
    id: int
    title: str
    time: int
    vod: int
    thumbnail: Optional[str]

class FullTextHit(BaseModel):
    """Full Text Search Hit Model"""
    id: int
    score: float
    highlights: List[str]
    type: str

class PublicSiteShow(BaseModel):
    """Public Site Show Model"""
    ShowId: int
    Title: str
    ThumbnailUrl: str
    VodUrl: str
    EmbedCode: str
    FieldDisplays: List[FieldDisplay]
    UpcomingRuns: List['PublicSiteScheduleItem']
    Chapters: List[VodChapter]
    Hit: Optional[FullTextHit]

class PublicSiteScheduleItem(BaseModel):
    """Public Site Schedule Item Model"""
    id: int
    ShowId: int
    StartTime: datetime
    EndTime: datetime
    Duration: int
    Channel: int

class PublicSiteShows(BaseModel):
    """Public Site Shows Collection"""
    Shows: List[PublicSiteShow]
    Meta: Dict[str, Any]

class PublicSiteGalleryPage(BaseModel):
    """Public Site Gallery Page Model"""
    CablecastGalleryId: int
    Title: str
    Page: int
    DisplayLimit: int
    Position: int
    Shows: List[PublicSiteShow]
    Meta: Dict[str, Any]

class VodConfiguration(BaseModel):
    """VOD Configuration Model"""
    id: int
    location: int
    providerName: str
    defaultQuality: int
    embedTemplate: str
    vodControlModuleSet: int
    vodTranscodeQualities: List[int]
    maximumResolution: int

class VodConfigurationResource(BaseModel):
    """Single VOD Configuration Resource Response"""
    vodConfiguration: VodConfiguration

class VodConfigurationsResource(BaseModel):
    """VOD Configurations Collection Response"""
    vodConfigurations: List[VodConfiguration]

class LogEntry(BaseModel):
    """Log Entry Model"""
    machineName: str
    logged: datetime
    level: str
    message: str
    logger: str
    exception: Optional[str]

class Option(BaseModel):
    """Option Model"""
    id: int
    name: str
    value: str

class OptionResource(BaseModel):
    """Single Option Resource Response"""
    option: Option

class OptionsResource(BaseModel):
    """Options Collection Response"""
    options: List[Option]

class MigrationStatus(BaseModel):
    """Migration Status Model"""
    status: int
    enabled: bool

class Channel(BaseModel):
    """Channel Model"""
    id: int
    name: str
    primaryLocation: int
    primaryOutput: int
    interstitialDwell: int
    liveStreams: List[int]
    channelContactInfo: int
    automationOverriden: bool
    brandingConfig: str
    squeezeBackEnabled: bool
    squeezeBackChannel: int
    squeezeBackBlock: int

class ChannelResource(BaseModel):
    """Single Channel Resource Response"""
    channel: Channel

class ChannelsResource(BaseModel):
    """Channels Collection Response with Meta"""
    meta: Dict[str, int]
    channels: List[Channel]

class ChannelResponse(BaseModel):
    """Channel HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class FieldOption(BaseModel):
    """Field Option Model"""
    id: int
    option: str
    fieldDefinition: int
    position: int

class FieldDefinition(BaseModel):
    """Field Definition Model"""
    id: int
    name: str
    type: str
    widget: str
    location: int
    fieldOptions: List[FieldOption]

class ShowField(BaseModel):
    """Show Field Model"""
    id: int
    label: str
    fieldDefinition: int
    maxInstances: int

class ShowFieldResource(BaseModel):
    """Single ShowField Resource Response"""
    showField: ShowField

class ShowFieldsResource(BaseModel):
    """ShowFields Collection Response"""
    showFields: List[ShowField]
    fieldDefinitions: List[FieldDefinition]

class Block(BaseModel):
    """Block Model"""
    id: int
    name: str
    offsets: List[int]
    location: int
    defaultSourceTime: datetime

class BlockResource(BaseModel):
    """Single Block Resource Response"""
    block: Block

class BlocksResource(BaseModel):
    """Blocks Collection Response"""
    blocks: List[Block]

class BlockResponse(BaseModel):
    """Block HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class AudioMeter(BaseModel):
    """Audio Meter Model"""
    value: int
    peak: int
    clipped: bool

class AudioLevel(BaseModel):
    """Audio Level Model"""
    left: float
    right: float
    sapLeft: float
    sapRight: float

class VideoServerMeterReading(BaseModel):
    """Video Server Meter Reading Model"""
    path: str
    audioLevel: AudioLevel

class DeviceStatus(BaseModel):
    """Device Status Model"""
    id: int
    device: int
    level: str
    errorDescription: Optional[str]
    action: str = "noOp"
    statusDescription: str
    positionInFrames: int
    frameRate: float
    droppedFrameCount: int
    filePath: str
    fileName: str
    automationOverriden: bool
    audioMeters: List[AudioMeter]
    encoderVideoPresent: bool
    encoderVideoResolutionValid: bool
    encoderConfiguredResolution: str
    encoderDetectedResolution: str
    decoderOutputResolution: str
    digitalFile: int
    isLegacy: bool
    networkStreamStatus: int
    transcribeActive: bool
    transcribeStart: datetime
    transcribeJob: str
    transcribeLanguage: str
    translationLanguage: str
    videoServerMeterReadings: List[VideoServerMeterReading]

class OutputPatch(BaseModel):
    """Output Patch Model"""
    id: int
    device: int
    output: int
    automationOverriden: bool

class PassthroughStatus(BaseModel):
    """Passthrough Status Model"""
    device: int
    id: int
    partners: List[int]
    passthroughRole: str

class RouterStatus(BaseModel):
    """Router Status Model"""
    level: str
    errorDescription: str

class AutomationStatus(BaseModel):
    """Automation Status Model"""
    deviceStatus: List[DeviceStatus]
    outputPatches: List[OutputPatch]
    passthroughStatus: List[PassthroughStatus]
    networkStreamStatus: List[NetworkStream]
    routerStatus: RouterStatus

class CustomField(BaseModel):
    """Custom Field Model"""
    id: int
    location: int
    customFieldNumber: str
    fieldName: str
    fieldType: str

class CustomFieldResource(BaseModel):
    """Single Custom Field Resource Response"""
    customField: CustomField

class CustomFieldsResource(BaseModel):
    """Custom Fields Collection Response"""
    customFields: List[CustomField]

class DeviceAction(BaseModel):
    """Device Action Model"""
    device: int
    action: str = "noOp"
    output: int
    chapter: int
    cue: int
    slot: int
    title: int
    fileKey: str
    streamUrl: str
    propertyName: str
    propertyValue: str
    transcribeLanguage: str
    translateLanguage: str

class SwitchEvent(BaseModel):
    """Switch Event Model"""
    device: int
    output: int

class AutomationOverride(BaseModel):
    """Automation Override Model"""
    override: bool
    output: int
    doLastSwitchOnResume: bool

class ForceEvent(BaseModel):
    """Force Event Model"""
    deviceAction: DeviceAction
    switchEvent: SwitchEvent
    automationOverride: AutomationOverride

class ForceEventsResource(BaseModel):
    """Force Events Resource"""
    forceEvents: List[ForceEvent]

class UserSession(BaseModel):
    """User Session Model"""
    user: str
    isAdmin: bool
    permissions: Dict[str, Dict[str, List[str]]]

class LiveStreamConfiguration(BaseModel):
    """Live Stream Configuration Model"""
    id: int
    publicBaseUrl: str
    reflectBaseUrl: str
    cablecastBaseUrl: str
    videoInput: str
    audioInput: str
    qualities: str
    embedTemplate: str
    inputResolution: str
    reflectEnabled: bool
    ipExemptPausedTemplate: str
    stoppedTemplate: str
    autoPlay: bool
    poster: int
    device: int

class LiveTransaction(BaseModel):
    """Live Transaction Model"""
    id: int
    liveStream: int
    state: str
    message: str
    timestamp: datetime
    user: str

class LiveStream(BaseModel):
    """Live Stream Model"""
    id: int
    location: int
    name: str
    channel: int
    transactions: List[int]
    state: str
    embedCode: str
    streamUrl: str
    nonReflectEmbedCode: str
    liveStreamConfiguration: int
    views: int
    autoPlay: bool

class LiveStreamResource(BaseModel):
    """Single LiveStream Resource Response"""
    liveStream: LiveStream

class LiveStreamsResource(BaseModel):
    """LiveStreams Collection Response"""
    liveStreams: List[LiveStream]
    liveTransactions: List[LiveTransaction]

class StateChangeRequest(BaseModel):
    """State Change Request Model"""
    newState: str

class ReleaseInvitation(BaseModel):
    """Release Invitation Model"""
    id: int
    releaseNotes: str
    releaseSummary: str
    version: str
    releaseDate: datetime
    status: int
    statusMessage: str
    releaseChannel: str
    serverUpdateStatuses: List[ServerUpdateStatus]

class ReleaseInvitationResource(BaseModel):
    """Single ReleaseInvitation Resource Response"""
    releaseInvitation: ReleaseInvitation

class ReleaseInvitationsResource(BaseModel):
    """ReleaseInvitations Collection Response"""
    releaseInvitations: List[ReleaseInvitation]

class CcsInfo(BaseModel):
    """CCS Info Model"""
    id: int
    name: str
    value: str

class CcsInfosResource(BaseModel):
    """CCS Infos Collection Response"""
    ccsInfos: List[CcsInfo]

class EventSummary(BaseModel):
    """Event Summary Model"""
    id: int
    showId: int
    channelId: int
    startTime: datetime
    endTime: datetime
    duration: int
    deleted: bool
    cgExempt: bool
    rerun: bool

class EventSummariesResource(BaseModel):
    """Event Summaries Collection Response"""
    meta: Dict[str, int]
    eventSummaries: List[EventSummary]

class LiveStreamQuality(BaseModel):
    """Live Stream Quality Model"""
    id: int
    name: str
    location: int
    settingsHash: str
    descriptionTemplate: str

class LiveStreamQualityResource(BaseModel):
    """Single LiveStreamQuality Resource Response"""
    liveStreamQuality: LiveStreamQuality

class LiveStreamQualitiesResource(BaseModel):
    """LiveStreamQualities Collection Response"""
    liveStreamQualities: List[LiveStreamQuality]

class OutputMirror(BaseModel):
    """Output Mirror Model"""
    id: int
    output: int
    destinationOutput: int

class Output(BaseModel):
    """Output Model"""
    id: int
    name: str
    location: int
    outputType: int
    outputNumber: int
    defaultInput: int
    active: bool
    fadeCms: int
    ratingCms: int
    primaryDevice: int
    useCablecastCgAsDefaultSource: bool
    outputPatch: int
    lBarEnabled: bool
    lBarBlock: int
    outputMirrors: List[OutputMirror]

class OutputResource(BaseModel):
    """Single Output Resource Response"""
    output: Output

class OutputsResource(BaseModel):
    """Outputs Collection Response"""
    outputs: List[Output]

class Thumbnail(BaseModel):
    """Thumbnail Model"""
    id: int
    slug: str
    url: str
    width: int
    height: int
    format: str

class ThumbnailResource(BaseModel):
    """Single Thumbnail Resource Response"""
    thumbnail: Optional[Thumbnail]

class FileUpload(BaseModel):
    """File Upload Model"""
    id: int
    fileName: str
    destinationStore: int
    state: int
    created: datetime
    lastModified: datetime
    totalSegments: int
    size: int

class FileUploadResource(BaseModel):
    """Single FileUpload Resource Response"""
    fileUpload: FileUpload

class FileUploadsResource(BaseModel):
    """FileUploads Collection Response"""
    fileUploads: List[FileUpload]

class FileUploadResponse(BaseModel):
    """FileUpload HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class ManualEvent(BaseModel):
    """Manual Event Model"""
    id: int
    location: int
    name: str
    length: int
    device: int
    deviceAction: int
    deviceSlot: int
    deviceTitle: int
    deviceChapter: int
    deviceCue: int
    deviceFileKey: str

class ManualEventResource(BaseModel):
    """Single ManualEvent Resource Response"""
    manualEvent: ManualEvent

class ManualEventsResource(BaseModel):
    """ManualEvents Collection Response"""
    manualEvents: List[ManualEvent]
    meta: Optional[Dict[str, int]]

class ManualEventResponse(BaseModel):
    """ManualEvent HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class License(BaseModel):
    """License Model"""
    licenseText: str

class LicenseResource(BaseModel):
    """License Resource Response"""
    licenseText: str

class DigitalFileLink(BaseModel):
    """Digital File Link Model"""
    id: int
    linkType: int
    reel: int
    digitalFile: int

class DigitalFileLinkResource(BaseModel):
    """Single DigitalFileLink Resource Response"""
    digitalFileLink: DigitalFileLink

class DigitalFileLinksResource(BaseModel):
    """DigitalFileLinks Collection Response"""
    digitalFileLinks: List[DigitalFileLink]

class Chapter(BaseModel):
    """Chapter Model"""
    id: int
    vod: int
    title: str
    body: str
    operatorNote: str
    offset: int
    quickAdded: bool
    order: int
    deleted: bool
    hidden: bool

class ChapterResource(BaseModel):
    """Single Chapter Resource Response"""
    chapter: Chapter

class ChaptersResource(BaseModel):
    """Chapters Collection Response"""
    chapters: List[Chapter]

class NdiSourcesResource(BaseModel):
    """NDI Sources Collection Response"""
    sources: List[str]

class SiteGallery(BaseModel):
    """Site Gallery Model"""
    id: int
    publicSite: int
    savedShowSearch: int
    position: int
    displayName: str
    displayLimit: int

class SiteGalleryResource(BaseModel):
    """Single SiteGallery Resource Response"""
    siteGallery: SiteGallery

class SiteGalleriesResource(BaseModel):
    """SiteGalleries Collection Response"""
    siteGalleries: List[SiteGallery]

class SiteGalleryResponse(BaseModel):
    """SiteGallery HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class PublicSiteSearch(BaseModel):
    """Public Site Search Model"""
    id: int
    publicSite: int
    savedShowSearch: int
    searchLimit: int
    position: int

class PublicSiteSearchResource(BaseModel):
    """Single PublicSiteSearch Resource Response"""
    publicSiteSearch: PublicSiteSearch

class PublicSiteSearchesResource(BaseModel):
    """PublicSiteSearches Collection Response"""
    publicSiteSearches: List[PublicSiteSearch]

class PublicSiteSearchResponse(BaseModel):
    """PublicSiteSearch HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class CrawlEvent(BaseModel):
    """Crawl Event Model"""
    id: int
    channel: int
    start: datetime
    length: int
    text: str
    deleted: bool

class CrawlEventResource(BaseModel):
    """Single CrawlEvent Resource Response"""
    crawlEvent: CrawlEvent

class CrawlEventsResource(BaseModel):
    """CrawlEvents Collection Response"""
    crawlEvents: List[CrawlEvent]

class ShowSearchSortingOption(BaseModel):
    """Show Search Sorting Option Model"""
    descending: bool
    field: str

class ShowSearchFilter(BaseModel):
    """Show Search Filter Model"""
    operator: str
    field: str
    showField: int
    searchValue: str

class ShowSearchGroup(BaseModel):
    """Show Search Group Model"""
    orAnd: str = "and"
    filters: List[ShowSearchFilter]

class ShowQuery(BaseModel):
    """Show Query Model"""
    sortOptions: List[ShowSearchSortingOption]
    groups: List[ShowSearchGroup]

class SavedShowSearch(BaseModel):
    """Saved Show Search Model"""
    id: int
    name: str
    query: ShowQuery
    results: List[int]

class SavedShowSearchResource(BaseModel):
    """Single SavedShowSearch Resource Response"""
    savedShowSearch: SavedShowSearch

class SavedShowSearchesResource(BaseModel):
    """SavedShowSearches Collection Response"""
    savedShowSearches: List[SavedShowSearch]
    shows: List[Show]

class Vod(BaseModel):
    """VOD Model"""
    id: int
    quality: int
    disabled: bool
    fileName: str
    length: Optional[int]
    embedCode: Optional[str]
    nonReflectEmbedCode: Optional[str]
    url: Optional[str]
    webVtt: Optional[str]
    localUrl: Optional[str]
    show: int
    stateChange: datetime
    stateProgress: float
    vodConfiguration: int
    chapters: List[int]
    chaptersPublished: bool
    chapteringSession: Optional[int]
    lastTransaction: int
    views: int
    transactionType: int
    percentComplete: float
    isOnCloud: bool
    vodState: str = "unknown"
    errorMessage: Optional[str]
    statusMessage: Optional[str]
    asset: Optional[int]
    isWatchable: bool
    usesAgendaLink: bool
    vodStatus: int

class VodResource(BaseModel):
    """Single VOD Resource Response"""
    vod: Vod

class VodsResource(BaseModel):
    """VODs Collection Response"""
    meta: Dict[str, int]
    vods: List[Vod]

class FirstRun(BaseModel):
    """First Run Model"""
    id: int
    show: int
    channel: int
    startTime: datetime
    endTime: datetime
    duration: int

class FirstRunResource(BaseModel):
    """Single FirstRun Resource Response"""
    firstRun: FirstRun

class FirstRunsResource(BaseModel):
    """FirstRuns Collection Response"""
    meta: Dict[str, int]
    firstRuns: List[FirstRun]

class SystemTimeInfo(BaseModel):
    """System Time Info Model"""
    time: datetime
    timeZone: str
    gmtOffset: float
    clientOffset: int
    ianaTimeZone: str

class SystemBaseSearch(BaseModel):
    """System Base Search Model"""
    id: int
    savedShowSearch: int
    searchLimit: int
    position: int

class SystemBaseSearchResource(BaseModel):
    """Single SystemBaseSearch Resource Response"""
    systemBaseSearch: SystemBaseSearch

class SystemBaseSearchesResource(BaseModel):
    """SystemBaseSearches Collection Response"""
    systemBaseSearches: List[SystemBaseSearch]

class VodTranscodeQuality(BaseModel):
    """VOD Transcode Quality Model"""
    id: int
    name: str
    vodProvider: int
    settingsHash: str
    descriptionTemplate: str

class VodTranscodeQualityResource(BaseModel):
    """Single VodTranscodeQuality Resource Response"""
    vodTranscodeQuality: VodTranscodeQuality

class VodTranscodeQualitiesResource(BaseModel):
    """VodTranscodeQualities Collection Response"""
    vodTranscodeQualities: List[VodTranscodeQuality]

class RaidInfo(BaseModel):
    """RAID Info Model"""
    id: int
    name: str
    server: int
    type: int
    status: int
    lastModified: datetime

class RaidInfoResource(BaseModel):
    """Single RaidInfo Resource Response"""
    raidInfo: RaidInfo

class RaidInfosResource(BaseModel):
    """RaidInfos Collection Response"""
    raidInfos: List[RaidInfo]

class Plugin(BaseModel):
    """Plugin Model"""
    id: str
    type: str
    config: Dict[str, Any]

class BatchShowAction(BaseModel):
    """Batch Show Action Model"""
    id: str
    type: str
    shows: List[int]

class BatchShowActionResource(BaseModel):
    """Batch Show Action Resource Response"""
    batchShowAction: BatchShowAction

class ServerSupportedMode(BaseModel):
    """Server Supported Mode Model"""
    mode: str = "None"
    friendlyLabel: str
    numOutputDevices: int
    numInputDevices: int

class ServerSupportedFeatures(BaseModel):
    """Server Supported Features Model"""
    serverModes: List[ServerSupportedMode]
    supportsVod: bool
    supportsLive: bool
    supportsCG: bool
    supportsVideoPlayback: bool

class Server(BaseModel):
    """Server Model"""
    id: int
    name: str
    version: str
    hostAddress: str
    lastUpdate: datetime
    timeDelta: int
    raidInfos: List[int]
    volumeInfos: List[int]
    remoteAccessId: str
    audioDevice: str
    volumeAdjustment: float
    serverModel: str
    availableAudioDevices: List[str]
    isVideoServer: bool

class ServerResource(BaseModel):
    """Single Server Resource Response"""
    server: Server
    raidInfos: List[RaidInfo]
    volumeInfos: List[VolumeInfo]

class ServersResource(BaseModel):
    """Servers Collection Response"""
    servers: List[Server]
    raidInfos: List[RaidInfo]
    volumeInfos: List[VolumeInfo]

class ServerConfiguration(BaseModel):
    """Server Configuration Model"""
    serverId: int
    locationId: int
    mode: str = "none"
    audioNormEnabled: bool
    additionalFileStores: List[int]
    routerOutputAddress: List[int]
    channelIds: List[str]
    channelRouterOutputAddress: List[int]
    routerInputAddress: List[int]
    useCgAsDefaultInput: List[bool]
    resolution: str

class ServerConnectionStatus(BaseModel):
    """Server Connection Status Model"""
    ok: bool
    message: str

class ServerConnectionStatusResource(BaseModel):
    """Server Connection Status Resource"""
    serverConnectionStatus: ServerConnectionStatus

class CaptionEditorCaptionTrack(BaseModel):
    """Caption Editor Caption Track Model"""
    language: str
    url: str
    type: str
    maxChars: int
    maxLines: int
    overlaps: bool
    illegalChars: bool

class CaptionEditorStyleGuide(BaseModel):
    """Caption Editor Style Guide Model"""
    name: str
    minDuration: float
    maxDuration: float
    maxChars: int
    maxLines: int
    overlaps: bool
    illegalChars: bool

class CaptionEditorLoadResponse(BaseModel):
    """Caption Editor Load Response Model"""
    mediaUrl: str
    thumbnailUrl: str
    mediaType: str
    aspectRatio: str
    captionTracks: List[CaptionEditorCaptionTrack]
    captionType: str
    publishEndpoint: str
    projectName: str
    frameRate: float
    dropFrame: bool
    promptToRetranslate: bool
    styleGuides: List[CaptionEditorStyleGuide]

class SystemSettings(BaseModel):
    """System Settings Model"""
    autoDatabaseBackupOptOut: bool

class SystemSettingsResource(BaseModel):
    """System Settings Resource"""
    systemSettings: SystemSettings

class Producer(BaseModel):
    """Producer Model"""
    id: int
    active: bool
    address: str
    contact: str
    email: str
    location: int
    notes: str
    phoneOne: str
    phoneTwo: str
    name: str
    website: str

class ProducerResource(BaseModel):
    """Single Producer Resource Response"""
    producer: Producer

class ProducersResource(BaseModel):
    """Producers Collection Response"""
    producers: List[Producer]

class ProducerResponse(BaseModel):
    """Producer HTTP Response"""
    version: Optional[str]
    statusCode: int
    reasonPhrase: Optional[str]
    isSuccessStatusCode: bool
    headers: Optional[Dict[str, List[str]]]
    content: Optional[Dict]

class Format(BaseModel):
    """Format Model"""
    id: int
    primitiveFormat: int
    name: str
    location: int

class FormatResource(BaseModel):
    """Single Format Resource Response"""
    format: Format

class FormatsResource(BaseModel):
    """Formats Collection Response"""
    formats: List[Format]

class Media(BaseModel):
    """Media Model"""
    id: int
    creationDate: datetime
    dispositionDate: datetime
    disposition: int
    format: int
    location: int
    mediaName: str
    preAssignedDevice: int
    preAssignedDeviceSlot: int
    overrideAspectRatio: int
    networkStream: int

class MediaResource(BaseModel):
    """Single Media Resource Response"""
    media: Media

class MediasResource(BaseModel):
    """Medias Collection Response"""
    media: List[Media]

class Gap(BaseModel):
    """Schedule Gap Model"""
    start: datetime
    end: datetime
    nextRunIsLocked: bool

class GapShowData(BaseModel):
    """Gap Show Data Model"""
    showID: int
    trt: int
    runCount: int
    cgExempt: bool

class FillerRun(BaseModel):
    """Filler Run Model"""
    showID: int
    runDateTime: datetime
    cgExempt: bool

class FillGapsJob(BaseModel):
    """Fill Gaps Job Model"""
    channel: int
    fillerSearch: int
    openSearch: int
    closeSearch: int
    preFillSearch: int
    postFillSearch: int
    fillMode: str = "completeFillWithRepeats"
    maximumBump: int
    start: datetime
    end: datetime

class FillGapJobResult(BaseModel):
    """Fill Gap Job Result Model"""
    fillMode: str
    gaps: List[Gap]
    fillerData: List[GapShowData]
    runs: List[FillerRun]
    scheduleItems: List[ScheduleItem]
    shows: List[Show]

class CompositorParams(BaseModel):
    """Compositor Parameters Model"""
    presentation_width: int
    presentation_height: int
    xpos: int
    ypos: int
    width: int
    height: int
    alpha: float
    zorder: int

class SetOverlayParams(BaseModel):
    """Set Overlay Parameters Model"""
    overlayId: str
    command: str
    assetTimestamp: datetime
    assetUrl: str
    animationDurationInSeconds: int
    compositorParams: CompositorParams
    text: str

class Event(BaseModel):
    """Event Model"""
    id: int
    controlModuleSet: int
    channel: int
    location: int
    schedule: int
    show: int
    reel: int
    media: int
    reelNumber: int
    eventDateTime: datetime
    routerControlModuleSet: int
    routerAction: int
    deviceControlModuleSet: int
    deviceAction: int
    action: str = "load"
    deviceRecordQuality: int
    cgCode: int
    setOverlayParams: Optional[SetOverlayParams]
    autopilotSend: int
    routerInputAddress: int
    routerOutputAddress: int
    routerTakeDevice: int
    routerTakeOutput: int
    device: int

class EventResource(BaseModel):
    """Single Event Resource Response"""
    event: Event

class EventsResource(BaseModel):
    """Events Collection Response"""
    events: List[Event]

class UserSettings(BaseModel):
    """User Settings Model"""
    id: str
    displayTwentyFourHourTime: bool
    defaultLocation: int
    defaultChannel: int
    deviceAssignmentsMode: str

class UserSettingsResource(BaseModel):
    """User Settings Resource Response"""
    userSettings: UserSettings

class SystemArchive(BaseModel):
    """System Archive Model"""
    serverId: int
    created: datetime
    failureMessage: str
    result: str

class SystemArchivesResource(BaseModel):
    """System Archives Collection Response"""
    systemArchives: List[SystemArchive]
  