/* RTP packet as defined in RFC 3984 - NOT USED YET! 
 *
 *     0                   1                   2                   3
 *     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 *     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *     |V=2|P|X|  CC=0 |M|     PT      |       sequence number         |
 *     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *     |                           timestamp                           |
 *     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 *     |           synchronization source (SSRC) identifier            |
 *     +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
 *
 *          +---------------+
 *          |0|1|2|3|4|5|6|7|
 *          +-+-+-+-+-+-+-+-+
 *          |F|NRI|  Type   |
 *          +---------------+
 *
 * */


struct rtppacket
{
		streamer_onebyte_t vpxcc;
		streamer_onebyte_t mpt;
		streamer_twobytes_t seqno;
		streamer_fourbytes_t timestamp;
		streamer_fourbytes_t ssrcid;
		streamer_onebyte_t payload[MAX_PAYLOAD];
} __attribute__ ((packed));

/* 90kHz clock as defined in RFC3984 */
#define STREAMER_RTP_CLOCK_FREQ 90000
#define STREAMER_RTP_MASK_M 0x80
#define STREAMER_RTP_MASK_PT 0x7F
#define STREAMER_RTP_DEFAULT_VPXCC 0x80
#define STREAMER_RTP_MBIT 0x80
#define STREAMER_RTP_STAPA_MPT 0x98   /* M bit set and packet type STAP-A == 24 == 0x18 */
#define STREAMER_RTP_DEFAULT_PT 0x5c
#define STREAMER_RTP_DEFAULT_SSRCID 0x0

/* RTP related defines at the moment are NOT USED in the program */

