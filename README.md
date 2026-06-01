# OffSight
Offsight is an end-to-end computer vision pipeline that automatically detects, tracks, and identifies football players in match footage.

It combines object detection, multi-object tracking, OCR, and appearance-based Re-ID to locate every player on the pitch, follow them as they move, and display their real names on screen — even when jersey numbers are hidden, blurred, or obscured.

Offsight identifies players primarily through jersey number recognition, but falls back to a layered system when numbers aren't visible — using player appearance (body shape, jersey color, kit details), positional continuity, and temporal majority voting to maintain robust identification through occlusion, camera cuts, and fast motion.

Built at the intersection of sports technology and applied AI, Offsight turns raw match footage into labeled, analyzable data for coaches, analysts, and broadcasters.
