import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/parking_area.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class ParkingDetailScreen extends StatefulWidget {
  final ParkingArea area;
  final bool showForecastOnly;
  final bool showRealtimeOnly;

  const ParkingDetailScreen({
    super.key,
    required this.area,
    this.showForecastOnly = false,
    this.showRealtimeOnly = false,
  });

  @override
  State<ParkingDetailScreen> createState() => _ParkingDetailScreenState();
}

class _ParkingDetailScreenState extends State<ParkingDetailScreen> {
  final ApiService _apiService = ApiService();
  Timer? _refreshTimer;

  // Prediction State
  DateTime _selectedDate = DateTime.now();
  TimeOfDay _selectedTime = TimeOfDay.now();
  bool _isPredicting = false;
  Map<String, dynamic>? _predictionResult;
  String _predictionError = '';

  // Realtime State
  Map<String, dynamic>? _realtimeStatus;
  bool _isLoadingRealtime = true;

  @override
  void initState() {
    super.initState();
    _fetchRealtimeStatus();
    _refreshTimer = Timer.periodic(const Duration(seconds: 2), (timer) {
      _fetchRealtimeStatus(showLoading: false);
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchRealtimeStatus({bool showLoading = true}) async {
    if (showLoading) setState(() => _isLoadingRealtime = true);
    try {
      final status = await _apiService.getRealtimeStatus(widget.area.id);
      if (mounted) {
        setState(() {
          _realtimeStatus = status;
          _isLoadingRealtime = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoadingRealtime = false);
    }
  }

  Future<void> _getPrediction() async {
    setState(() {
      _isPredicting = true;
      _predictionError = '';
      _predictionResult = null;
    });

    try {
      final dateTime = DateTime(
        _selectedDate.year,
        _selectedDate.month,
        _selectedDate.day,
        _selectedTime.hour,
        _selectedTime.minute,
      );

      final result = await _apiService.getPrediction(widget.area.id, dateTime);
      setState(() {
        _predictionResult = result;
      });
    } catch (e) {
      setState(() {
        _predictionError = e.toString();
      });
    } finally {
      setState(() {
        _isPredicting = false;
      });
    }
  }

  Future<void> _launchMaps(double lat, double lng) async {
    final url = Uri.parse(
      'https://www.google.com/maps/search/?api=1&query=$lat,$lng',
    );
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Could not launch maps')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text(widget.area.name),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [AppTheme.backgroundBlack, Color(0xFF1A1A1E)],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(
            top: 120.0,
            left: 16.0,
            right: 16.0,
            bottom: 40.0,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildAreaInfo(),
              const SizedBox(height: 24),
              if (!widget.showRealtimeOnly) ...[
                _buildPredictionSection(),
                const SizedBox(height: 32),
              ],
              if (!widget.showForecastOnly) _buildRealtimeSection(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAreaInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                widget.area.description,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
            GlassCard(
              borderRadius: 12,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.star, color: Colors.amber, size: 16),
                  const SizedBox(width: 4),
                  const Text(
                    '4.8',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPredictionSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Availability Forecast',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        GlassCard(
          borderRadius: 24,
          child: Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: GestureDetector(
                      onTap: () async {
                        final date = await showDatePicker(
                          context: context,
                          initialDate: _selectedDate,
                          firstDate: DateTime.now(),
                          lastDate: DateTime.now().add(
                            const Duration(days: 30),
                          ),
                        );
                        if (date != null) setState(() => _selectedDate = date);
                      },
                      child: _buildPickerButton(
                        Icons.calendar_month,
                        DateFormat('MMM dd, yyyy').format(_selectedDate),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: GestureDetector(
                      onTap: () async {
                        final time = await showTimePicker(
                          context: context,
                          initialTime: _selectedTime,
                        );
                        if (time != null) setState(() => _selectedTime = time);
                      },
                      child: _buildPickerButton(
                        Icons.access_time,
                        _selectedTime.format(context),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isPredicting ? null : _getPrediction,
                  child: _isPredicting
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.black,
                          ),
                        )
                      : const Text('Check Availability'),
                ),
              ),
              if (_predictionError.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Text(
                    _predictionError,
                    style: const TextStyle(
                      color: AppTheme.errorRed,
                      fontSize: 12,
                    ),
                  ),
                ),
              if (_predictionResult != null) _buildPredictionData(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPickerButton(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 16, color: AppTheme.neonCyan),
          const SizedBox(width: 8),
          Text(
            text,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionData() {
    final freeSlots = _predictionResult!['free_slots'] as List;
    return Column(
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 20),
          child: Divider(color: Colors.white12),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildConfidenceGauge(0.93), // Hardcoded 93% from our training
            const SizedBox(width: 32),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Prediction',
                  style: TextStyle(color: Colors.white54, fontSize: 12),
                ),
                Text(
                  '${freeSlots.length} Slots Likely Free',
                  style: const TextStyle(
                    color: AppTheme.neonEmerald,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Confidence: 93%',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.3),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 20),
        if (freeSlots.isNotEmpty)
          Wrap(
            spacing: 8,
            children: freeSlots
                .map(
                  (id) => Chip(
                    label: Text(
                      'Slot $id',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    backgroundColor: AppTheme.neonEmerald.withOpacity(0.1),
                    side: const BorderSide(
                      color: AppTheme.neonEmerald,
                      width: 0.5,
                    ),
                  ),
                )
                .toList(),
          )
        else
          const Text(
            'High occupancy predicted.',
            style: TextStyle(color: AppTheme.errorRed, fontSize: 13),
          ),
      ],
    );
  }

  Widget _buildConfidenceGauge(double val) {
    return Stack(
      alignment: Alignment.center,
      children: [
        SizedBox(
          height: 70,
          width: 70,
          child: CircularProgressIndicator(
            value: val,
            strokeWidth: 8,
            color: AppTheme.neonCyan,
            backgroundColor: Colors.white10,
          ),
        ),
        Text(
          '${(val * 100).toInt()}%',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildRealtimeSection() {
    // 1. Calculate Aggregate Stats
    int totalSlots = widget.area.slots.length;
    int freeCount = 0;
    int occupiedCount = 0;

    final List<Map<String, dynamic>> processedSlots = widget.area.slots.map((
      slot,
    ) {
      String status = 'analyzing';
      bool isFree = false;

      if (_realtimeStatus != null && _realtimeStatus!.containsKey('slots')) {
        final slotsData = _realtimeStatus!['slots'];
        if (slotsData is Map) {
          final slotKey = slot.id.toString();
          if (slotsData.containsKey(slotKey)) {
            final slotInfo = slotsData[slotKey];
            if (slotInfo is Map && slotInfo.containsKey('status')) {
              final rawStatus = slotInfo['status'].toString().toLowerCase();
              status = rawStatus;
              isFree =
                  (rawStatus == 'free' ||
                  rawStatus == '0' ||
                  rawStatus == 'unoccupied');
            }
          }
        }
      }

      if (isFree)
        freeCount++;
      else
        occupiedCount++;
      return {'slot': slot, 'status': status, 'isFree': isFree};
    }).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Real-time Status',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            _isLoadingRealtime
                ? const SizedBox(
                    height: 16,
                    width: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : IconButton(
                    icon: const Icon(
                      Icons.refresh,
                      size: 20,
                      color: Colors.white54,
                    ),
                    onPressed: _fetchRealtimeStatus,
                  ),
          ],
        ),
        const SizedBox(height: 16),

        // 2. Summary Dashboard
        _buildStatusSummary(totalSlots, freeCount, occupiedCount),
        const SizedBox(height: 24),

        // 3. Grid of Slots
        if (_realtimeStatus == null && !_isLoadingRealtime)
          const Center(child: Text('Live data sync paused.'))
        else
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.1,
            ),
            itemCount: processedSlots.length,
            itemBuilder: (context, index) {
              final data = processedSlots[index];
              return _buildCompactSlotCard(data);
            },
          ),
      ],
    );
  }

  Widget _buildStatusSummary(int total, int free, int occupied) {
    double completion = total > 0 ? (free / total) : 0;

    return GlassCard(
      borderRadius: 24,
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          _buildConfidenceGauge(
            completion,
          ), // Reusing our gauge widget for occupancy
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildStatRow(
                  Icons.local_parking,
                  'Total Slots',
                  total.toString(),
                  Colors.white54,
                ),
                const SizedBox(height: 8),
                _buildStatRow(
                  Icons.check_circle,
                  'Available',
                  free.toString(),
                  AppTheme.neonEmerald,
                ),
                const SizedBox(height: 8),
                _buildStatRow(
                  Icons.block,
                  'Occupied',
                  occupied.toString(),
                  AppTheme.errorRed,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(IconData icon, String label, String value, Color color) {
    return Row(
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.white30),
        ),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildCompactSlotCard(Map<String, dynamic> data) {
    final slot = data['slot'] as ParkingSlot;
    final bool isFree = data['isFree'];
    final String status = data['status'];
    final Color stateColor = isFree ? AppTheme.neonEmerald : AppTheme.errorRed;

    return GlassCard(
      borderRadius: 20,
      padding: const EdgeInsets.all(12),
      color: stateColor,
      opacity: 0.1, // Slightly higher opacity to show the color better
      border: Border.all(color: stateColor.withOpacity(0.3), width: 1.5),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 8),
          Text(
            'Slot ${slot.id}',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 4),
          Text(
            status.toUpperCase(),
            style: TextStyle(
              color: stateColor.withOpacity(0.7),
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => _launchMaps(slot.lat, slot.lng),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.white10),
              ),
              child: const Text(
                'NAVIGATE',
                style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
