import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final AuthService _auth = AuthService();
  final _formKey = GlobalKey<FormState>();

  String email = '';
  String password = '';
  String fullName = '';
  String licensePlate = '';
  String phoneNumber = '';
  String error = '';
  bool isLoading = false;

  Future<void> _handleRegister() async {
    if (_formKey.currentState!.validate()) {
      setState(() => isLoading = true);
      try {
        await _auth.register(
          email: email,
          password: password,
          fullName: fullName,
          licensePlate: licensePlate,
          phoneNumber: phoneNumber,
        );
        if (mounted) Navigator.pop(context); // Go back to login
      } catch (e) {
        setState(() {
          error = 'Registration failed. Try a different email.';
          isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topRight,
            end: Alignment.bottomLeft,
            colors: [Color(0xFF0D1B2A), Color(0xFF000000)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Custom Back Button
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(
                        Icons.arrow_back_ios_new,
                        color: Colors.white,
                        size: 20,
                      ),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    children: [
                      Text(
                        'Join DriveInSight',
                        style: Theme.of(context).textTheme.headlineLarge,
                      ),
                      const SizedBox(height: 32),

                      GlassCard(
                        borderRadius: 32,
                        padding: const EdgeInsets.all(24),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _buildTextField(
                                label: 'Full Name',
                                icon: Icons.person_outline,
                                onChanged: (val) => fullName = val,
                                validator: (val) =>
                                    val!.isEmpty ? 'Enter name' : null,
                              ),
                              const SizedBox(height: 16),
                              _buildTextField(
                                label: 'Email',
                                icon: Icons.email_outlined,
                                onChanged: (val) => email = val,
                                validator: (val) =>
                                    val!.isEmpty ? 'Enter email' : null,
                              ),
                              const SizedBox(height: 16),
                              _buildTextField(
                                label: 'License Plate (e.g. ABC 1234)',
                                icon: Icons.directions_car_outlined,
                                onChanged: (val) => licensePlate = val,
                                validator: (val) =>
                                    val!.isEmpty ? 'Enter license plate' : null,
                              ),
                              const SizedBox(height: 16),
                              _buildTextField(
                                label: 'Phone Number',
                                icon: Icons.phone_android_outlined,
                                onChanged: (val) => phoneNumber = val,
                                validator: (val) =>
                                    val!.isEmpty ? 'Enter phone' : null,
                              ),
                              const SizedBox(height: 16),
                              _buildTextField(
                                label: 'Password',
                                icon: Icons.lock_outline,
                                isPassword: true,
                                onChanged: (val) => password = val,
                                validator: (val) => val!.length < 6
                                    ? '6+ characters required'
                                    : null,
                              ),
                              if (error.isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(top: 16),
                                  child: Text(
                                    error,
                                    style: const TextStyle(
                                      color: AppTheme.errorRed,
                                      fontSize: 13,
                                    ),
                                  ),
                                ),
                              const SizedBox(height: 32),
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton(
                                  onPressed: isLoading ? null : _handleRegister,
                                  child: isLoading
                                      ? const SizedBox(
                                          height: 20,
                                          width: 20,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            color: Colors.black,
                                          ),
                                        )
                                      : const Text('CREATE ACCOUNT'),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 48),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required String label,
    required IconData icon,
    bool isPassword = false,
    required Function(String) onChanged,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 13),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white10),
          ),
          child: TextFormField(
            obscureText: isPassword,
            onChanged: onChanged,
            validator: validator,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              prefixIcon: Icon(icon, color: AppTheme.neonCyan, size: 20),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                vertical: 16,
                horizontal: 16,
              ),
            ),
          ),
        ),
      ],
    );
  }
}
