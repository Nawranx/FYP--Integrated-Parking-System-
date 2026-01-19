import 'dart:async';
import 'package:flutter/material.dart';
import '../models/parking_area.dart';
import '../services/api_service.dart';
import '../screens/parking_detail_screen.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class SmartSuggestionTab extends StatefulWidget {
  const SmartSuggestionTab({super.key});

  @override
  State<SmartSuggestionTab> createState() => _SmartSuggestionTabState();
}

class _SmartSuggestionTabState extends State<SmartSuggestionTab> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();

  bool _isSearching = false;
  bool _showResults = false;
  List<ParkingArea> _areas = [];
  bool _isLoading = false;
  bool _isArea1Full = false;
  bool _isArea2Full = false;
  Timer? _refreshTimer;

  // Simulation Data for "Plaza Mall"
  final String _targetLocation = "Plaza Mall";

  // Distances in meters
  final Map<String, int> _distances = {"area1": 100, "area2": 500};

  @override
  void dispose() {
    _searchController.dispose();
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _updateLiveStatuses() async {
    if (_areas.isEmpty) return;

    bool area1Full = false;
    bool area2Full = false;

    for (var area in _areas) {
      try {
        final liveData = await _apiService.getRealtimeStatus(area.id);
        final bool isFull = (liveData['free_slots'] ?? 0) <= 0;
        if (area.id.toLowerCase() == "area1") {
          area1Full = isFull;
        } else if (area.id.toLowerCase() == "area2") {
          area2Full = isFull;
        }
      } catch (e) {
        print('DEBUG: Error updating status for ${area.id}: $e');
      }
    }

    if (mounted) {
      setState(() {
        _isArea1Full = area1Full;
        _isArea2Full = area2Full;
      });
    }
  }

  Future<void> _handleSearch(String query) async {
    final sanitizedQuery = query.trim().toLowerCase();

    // Check if query contains target location keywords
    if (sanitizedQuery.isEmpty ||
        !sanitizedQuery.contains(_targetLocation.split(' ')[0].toLowerCase())) {
      setState(() {
        _showResults = false;
        _isSearching = sanitizedQuery.isNotEmpty;
      });
      _refreshTimer?.cancel();
      return;
    }

    setState(() {
      _isLoading = true;
      _isSearching = true;
      _showResults = false;
    });

    _refreshTimer?.cancel();

    try {
      print('DEBUG: Fetching areas for Smart Suggestion...');
      final areas = await _apiService.getAreas();

      if (mounted) {
        setState(() {
          _areas = areas;
          _isLoading = false;
          _showResults = true;
        });

        // Initial status update
        await _updateLiveStatuses();

        // Set up periodic refresh every 3 seconds
        _refreshTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
          _updateLiveStatuses();
        });
      }
    } catch (e) {
      print('DEBUG: Search Error: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
          _showResults = false;
        });
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 40),
          Text(
            'Smart Suggestion',
            style: Theme.of(context).textTheme.headlineLarge,
          ),
          const SizedBox(height: 8),
          const Text(
            'Prioritizing convenience and reducing your search time.',
            style: TextStyle(color: Colors.white60),
          ),
          const SizedBox(height: 32),

          _buildSearchField(),

          const SizedBox(height: 32),

          if (_isLoading)
            const Center(
              child: CircularProgressIndicator(color: AppTheme.neonCyan),
            )
          else if (_showResults)
            Expanded(child: _buildResultsList())
          else if (_isSearching && !_showResults)
            const Center(
              child: Text(
                'No nearby areas found for this location.',
                style: TextStyle(color: Colors.white38),
              ),
            )
          else
            _buildEmptyState(),
        ],
      ),
    );
  }

  Widget _buildSearchField() {
    return GlassCard(
      borderRadius: 20,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: TextField(
        controller: _searchController,
        style: const TextStyle(color: Colors.white),
        onSubmitted: _handleSearch,
        decoration: InputDecoration(
          hintText: 'Search destination (e.g. Plaza Mall)',
          hintStyle: const TextStyle(color: Colors.white30),
          prefixIcon: const Icon(
            Icons.location_on_outlined,
            color: AppTheme.neonCyan,
          ),
          suffixIcon: IconButton(
            icon: const Icon(Icons.search, color: AppTheme.neonCyan),
            onPressed: () => _handleSearch(_searchController.text),
          ),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(vertical: 20),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        children: [
          const SizedBox(height: 60),
          Icon(
            Icons.auto_awesome,
            size: 60,
            color: AppTheme.neonCyan.withOpacity(0.2),
          ),
          const SizedBox(height: 16),
          const Text(
            'Enter your destination to find the\nbest parking spot for you.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white38),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsList() {
    // Sort areas by distance (Area 1 at 100m, Area 2 at 500m)
    // In a real app, we'd use GPS. For this objective, we use the simulation data.

    // Safety check for areas
    ParkingArea? area1;
    ParkingArea? area2;

    for (var a in _areas) {
      if (a.id.toLowerCase() == "area1") area1 = a;
      if (a.id.toLowerCase() == "area2") area2 = a;
    }

    if (area1 == null || area2 == null) {
      return const Center(
        child: Text(
          "Could not retrieve parking area data.",
          style: TextStyle(color: Colors.white38),
        ),
      );
    }

    return ListView(
      children: [
        const Text(
          'Nearby Results for Plaza Mall',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),

        if (_isArea1Full)
          _buildAlert(
            'Zone A is just 100m away, but it is currently fully occupied. We suggest using Zone B to save your time.',
          ),

        const SizedBox(height: 16),

        _buildAreaCard(area1, _distances["area1"]!, isOccupied: _isArea1Full),
        const SizedBox(height: 16),
        _buildAreaCard(
          area2,
          _distances["area2"]!,
          isOccupied: _isArea2Full,
          isSuggested: _isArea1Full,
        ),
      ],
    );
  }

  Widget _buildAlert(String message) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.neonCyan.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.neonCyan.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.info_outline, color: AppTheme.neonCyan, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: AppTheme.neonCyan,
                fontSize: 13,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAreaCard(
    ParkingArea area,
    int distance, {
    bool isOccupied = false,
    bool isSuggested = false,
  }) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) =>
                ParkingDetailScreen(area: area, showRealtimeOnly: true),
          ),
        );
      },
      child: Stack(
        children: [
          GlassCard(
            borderRadius: 24,
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: (isOccupied ? AppTheme.errorRed : AppTheme.neonCyan)
                        .withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    isOccupied ? Icons.block : Icons.local_parking,
                    color: isOccupied ? AppTheme.errorRed : AppTheme.neonCyan,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        area.name,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        '$distance meters away',
                        style: const TextStyle(
                          color: Colors.white30,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      isOccupied ? 'FULL' : 'AVAILABLE',
                      style: TextStyle(
                        color: isOccupied
                            ? AppTheme.errorRed
                            : AppTheme.neonEmerald,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const Icon(
                      Icons.arrow_forward_ios,
                      color: Colors.white24,
                      size: 14,
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (isSuggested)
            Positioned(
              top: 0,
              right: 20,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: const BoxDecoration(
                  color: AppTheme.neonEmerald,
                  borderRadius: BorderRadius.only(
                    bottomLeft: Radius.circular(8),
                    bottomRight: Radius.circular(8),
                  ),
                ),
                child: const Text(
                  'SUGGESTED',
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
