# 21 · Case study — Chat / messaging (fan-out, ordering, delivery semantics, presence)

> Phase-1 brief (NO course prose). Bespoke walkthrough. Math RECOMPUTED in `_recompute.py`
> (Case 3). Exercises persistent connections, per-conversation ordering (11/17), delivery
> semantics (17), and group fan-out (14/17).

## 1. Requirements
- **Functional:** 1:1 and group messaging; ordered delivery within a conversation; delivery +
  read receipts; presence (online/typing); offline message storage + sync on reconnect; push
  notifications.
- **Non-functional:** send->deliver p99 < 500 ms when both online; no message loss (at-least-once
  with dedup); per-conversation total order; persistent connections at scale.
- **Scale (RECOMPUTED, Case 3):** 50M DAU, 40 msgs/user/day -> **~23,148 msg QPS** (peak ~46k);
  100 B/msg -> **~73 TB/yr**; 50M concurrent websockets / 50k per gateway -> **1,000 gateway
  nodes**; a 500-member group send = **500 delivery events**.

## 2. Data model + API
- **Model:** `messages {conversation_id, seq, sender, body, ts}` (partitioned by
  `conversation_id`, ordered by a per-conversation monotonic `seq`); `conversation_members`;
  `user_inbox/cursor {user_id, conversation_id, last_delivered_seq, last_read_seq}`.
- **API (mostly over a websocket):** `send(conversation_id, client_msg_id, body)`;
  `ack(conversation_id, seq)`; `subscribe(conversations)`; `presence(state)`. `client_msg_id` is
  the **idempotency key** for dedup.
- **Ordering:** a per-conversation `seq` assigned by the conversation's owning partition (reuse 11:
  ordering needs a single sequencer per conversation; a per-partition log, reuse 09/17, gives total
  order within the conversation without global ordering).

## 3. Bottleneck analysis
- **Persistent-connection footprint, not raw QPS, is the scaling axis:** 50M live websockets ->
  1,000 gateway nodes (RECOMPUTED); a connection registry maps `user_id -> gateway` so a message
  can be routed to the recipient's current socket.
- **Group fan-out:** a send to a 500-member group becomes 500 routing+delivery events — a smaller,
  bounded version of the feed fan-out (Case 2); the same push-vs-pull logic applies for very large
  groups/channels (huge channels -> pull/read-time).
- **Write path:** 23k msg QPS is modest; the hard part is **ordering + exactly-once-effect +
  presence churn**, not throughput.

## 4. Design + cross-links to 13-20
- **13:** sizing shows connections (1,000 gateways) dominate; message QPS is easy.
- **14:** partition messages + the sequencer by `conversation_id`; large channels are a hot
  partition -> read-time fan-out (14 hot-key pattern, same as Case 2 celebrity).
- **15:** message history is durable + replicated; ordering within a conversation needs a single
  writer (the partition leader) -> a 15 single-leader-per-partition topology; cross-conversation
  needs no global order.
- **16:** recent-message and presence state cached at the edge/gateway; conversation metadata
  cached.
- **17:** the **core** — at-least-once delivery + dedup on `client_msg_id` -> exactly-once-EFFECT;
  per-conversation log gives ordering; offline users get messages persisted and replayed on
  reconnect (consumer cursor = `last_delivered_seq`, reuse 17 consumer offset).
- **18:** presence/typing events are high-volume + low-value -> rate-limit + shed first under load;
  bounded per-connection send queues (backpressure to a flooding client).
- **19:** send->deliver latency, delivery-success ratio, connection count, presence fan-out rate =
  golden signals.
- **20:** gateway node death = reconnect to another node + resync from cursor (no message loss);
  degrade presence before messages; the durable log makes delivery replayable.

## 5. Failure modes (20)
- **Gateway crash:** clients reconnect to a healthy gateway; the connection registry updates;
  undelivered messages replay from `last_delivered_seq` -> no loss (at-least-once + dedup).
- **Duplicate delivery:** network retry re-sends -> recipient dedups on `client_msg_id`/`seq`.
- **Out-of-order arrival:** client buffers by `seq` and reorders (per-conversation total order is
  authoritative).
- **Presence storm (mass reconnect after a network blip):** thundering reconnect = a retry storm
  (18) -> jittered backoff + presence shed; messages prioritized over presence.
- **Large-channel hot partition:** switch that channel to read-time fan-out.

## 6. Tradeoffs
- **Per-conversation order vs throughput:** a single sequencer per conversation caps that
  conversation's write rate but is essentially never the bottleneck (humans are slow); global
  ordering would be far costlier and is unnecessary (11).
- **Push vs pull for groups:** small groups push (cheap); mega-channels pull (avoid fan-out
  storm) — same trade as Case 2.
- **Delivery semantics:** exactly-once *transport* is impossible (FLP/2-generals, reuse 11) ->
  at-least-once + idempotent apply = exactly-once *effect* (17). This is the honest framing.
- **Presence accuracy vs cost:** precise presence is chatty; coarse/approximate presence (heartbeat
  windows) trades freshness for far less load.

## 7. Sources / gaps
- **REUSED (line-verified):** 11 (ordering/sequencer, no global clock, FLP, 2-generals -> no true
  exactly-once transport), 13 (connection sizing), 14 (conversation partitioning, hot channel),
  15 (single-leader-per-partition for order, durable replication), 16 (recent/presence cache),
  17 (at-least-once + dedup = exactly-once-effect, consumer cursor, replay, per-partition order),
  18 (presence shedding, reconnect storm backpressure), 19 (golden signals), 20 (reconnect+resync,
  degrade presence).
- **RECOMPUTED:** msg QPS, storage/yr, gateway node count, group fan-out.
- **`[UNVERIFIED]`:** websocket/XMPP/MQTT protocol specifics + vendor chat designs (WhatsApp/Signal
  eng talks) not fetched; mechanisms grounded in 11/17. Per-conversation sequencer is the 09/17 log
  applied, not a new primitive.
