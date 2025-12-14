package com.resumeos.auth_service.service;

import com.resumeos.auth_service.dto.AuthenticationRequest;
import com.resumeos.auth_service.dto.AuthenticationResponse;
import com.resumeos.auth_service.dto.RegisterRequest;
import com.resumeos.auth_service.entity.Role;
import com.resumeos.auth_service.entity.User;
import com.resumeos.auth_service.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthenticationService {

    private final UserRepository repository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    public AuthenticationResponse register(RegisterRequest request) {
        // 1. Sanitize the role string from React
        // React sends "service-manager", we need "SERVICE_MANAGER"
        String sanitizedRole = request.getRole()
                .replace("-", "_")
                .toUpperCase();

        // 2. Convert to Enum (Default to USER if invalid)
        Role userRole;
        try {
            userRole = Role.valueOf(sanitizedRole);
        } catch (IllegalArgumentException | NullPointerException e) {
            userRole = Role.USER; // Fallback
        }

        // 3. Create the User entity with ALL fields
        var user = User.builder()
                .fullName(request.getFullName())        // <-- Added
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .location(request.getLocation())        // <-- Added
                .plant(request.getPlant())              // <-- Added
                .role(userRole)                         // <-- Updated
                .build();

        repository.save(user);

        // 4. Generate Token immediately so they don't have to login again
        var jwtToken = jwtService.generateToken(user);
        return AuthenticationResponse.builder()
                .token(jwtToken)
                .build();
    }

    public AuthenticationResponse authenticate(AuthenticationRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );

        var user = repository.findByEmail(request.getEmail())
                .orElseThrow();

        var jwtToken = jwtService.generateToken(user);

        return AuthenticationResponse.builder()
                .token(jwtToken)
                .build();
    }
}