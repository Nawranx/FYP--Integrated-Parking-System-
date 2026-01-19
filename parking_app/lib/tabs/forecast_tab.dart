import 'package:flutter/material.dart';
import '../models/parking_area.dart';
import '../services/api_service.dart';
import '../screens/parking_detail_screen.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class ForecastTab extends StatefulWidget {
  const ForecastTab({super.key});

  @override
  State<ForecastTab> createState() => _ForecastTabState();
}

class _ForecastTabState extends State<ForecastTab> {
  final ApiService _apiService = ApiService();
  List<ParkingArea> _allAreas = [];
  List<ParkingArea> _filteredAreas = [];
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _fetchAreas();
  }

  Future<void> _fetchAreas() async {
    try {
      final areas = await _apiService.getAreas();
      setState(() {
        _allAreas = areas;
        _filteredAreas = areas;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  void _filterAreas(String query) {
    if (query.isEmpty) {
      setState(() {
        _filteredAreas = _allAreas;
      });
      return;
    }

    final sanitizedQuery = query.toLowerCase().trim();
    final isPlazaMall =
        sanitizedQuery.contains('plaza') || sanitizedQuery.contains('mall');

    setState(() {
      _filteredAreas = _allAreas.where((area) {
        if (isPlazaMall) return true; // Show all areas for plaza mall search
        return area.name.toLowerCase().contains(sanitizedQuery);
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: RadialGradient(
          center: const Alignment(-0.8, -0.6),
          radius: 1.0,
          colors: [AppTheme.neonCyan.withOpacity(0.05), Colors.transparent],
        ),
      ),
      child: CustomScrollView(
        slivers: [
          _buildHeader(),
          _buildSearchBar(),
          _buildAreasGrid(),
          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      sliver: SliverToBoxAdapter(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AI Forecaster',
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            const SizedBox(height: 8),
            const Text(
              'Search locations to view predicted availability for the next 30 days.',
              style: TextStyle(color: Colors.white60),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      sliver: SliverToBoxAdapter(
        child: GlassCard(
          borderRadius: 20,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: TextField(
            onChanged: _filterAreas,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              hintText: 'Where are you going?',
              hintStyle: TextStyle(color: Colors.white30),
              prefixIcon: Icon(Icons.search, color: AppTheme.neonCyan),
              border: InputBorder.none,
              contentPadding: EdgeInsets.symmetric(vertical: 20),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAreasGrid() {
    if (_isLoading) {
      return const SliverFillRemaining(
        child: Center(
          child: CircularProgressIndicator(color: AppTheme.neonCyan),
        ),
      );
    }

    if (_error.isNotEmpty) {
      return SliverFillRemaining(
        child: Center(
          child: Text(
            'Error: $_error',
            style: const TextStyle(color: AppTheme.errorRed),
          ),
        ),
      );
    }

    return SliverPadding(
      padding: const EdgeInsets.all(20),
      sliver: SliverGrid(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 20,
          crossAxisSpacing: 20,
          childAspectRatio: 0.8,
        ),
        delegate: SliverChildBuilderDelegate((context, index) {
          final area = _filteredAreas[index];
          return _buildAreaCard(area);
        }, childCount: _filteredAreas.length),
      ),
    );
  }

  Widget _buildAreaCard(ParkingArea area) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) =>
                ParkingDetailScreen(area: area, showForecastOnly: true),
          ),
        );
      },
      child: GlassCard(
        borderRadius: 24,
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.neonCyan.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.local_parking,
                color: AppTheme.neonCyan,
                size: 24,
              ),
            ),
            const Spacer(),
            Text(
              area.name,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${area.slots.length} Slots',
              style: const TextStyle(color: Colors.white30, fontSize: 12),
            ),
            const SizedBox(height: 12),
            // Occupancy Indicator (Dummy for now)
            Row(
              children: [
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: const LinearProgressIndicator(
                      value: 0.85,
                      backgroundColor: Colors.white10,
                      valueColor: AlwaysStoppedAnimation(AppTheme.neonEmerald),
                      minHeight: 4,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                const Text(
                  '85%',
                  style: TextStyle(
                    color: AppTheme.neonEmerald,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
