package com.resumeos.auth_service.repository;

import com.resumeos.auth_service.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    // Spring generates the SQL for this automatically
    Optional<User> findByEmail(String email);
}
