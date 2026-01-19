class ParkingSlot {
  final String id;
  final double lat;
  final double lng;

  ParkingSlot({required this.id, required this.lat, required this.lng});

  factory ParkingSlot.fromJson(String id, Map<String, dynamic> json) {
    return ParkingSlot(
      id: id,
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
    );
  }
}

class ParkingArea {
  final String id;
  final String name;
  final String description;
  final double lat;
  final double lng;
  final List<ParkingSlot> slots;

  ParkingArea({
    required this.id,
    required this.name,
    required this.description,
    required this.lat,
    required this.lng,
    required this.slots,
  });

  factory ParkingArea.fromJson(String id, Map<String, dynamic> json) {
    var rawSlots = json['slots'] as Map<String, dynamic>? ?? {};
    List<ParkingSlot> parsedSlots = [];
    rawSlots.forEach((key, value) {
      parsedSlots.add(ParkingSlot.fromJson(key, value));
    });

    // Sort slots by ID if they are numeric
    parsedSlots.sort((a, b) => int.parse(a.id).compareTo(int.parse(b.id)));

    return ParkingArea(
      id: id,
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      lat: (json['location']['lat'] as num).toDouble(),
      lng: (json['location']['lng'] as num).toDouble(),
      slots: parsedSlots,
    );
  }
}
