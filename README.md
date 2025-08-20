# Housni Job Portal

This is the backend of the Housni Job Portal. The system is designed to help recruiters manage open positions and
candidates apply for positions.

## Project outline

- Authentication and authorization: The system uses JWT tokens for authentication and authorization.
- Roles: The system has 3 roles: Admin, Recruiter, and Candidate.
- **Admin**:
    - Can manage users (add, delete, update).
    - Can View all resumes of candidates (with the option to download).
    - Can filter candidates based on their skills and experience.
- **Recruiter**:
    - Can manage open positions (add, delete, update).
    - Can view all candidates who have applied for a position.
    - Can filter candidates based on their skills and experience.
    - Can shortlist candidates by changing the status of their application.
- **Candidate**:
    - Can view all open positions.
    - Can apply for a position.
    - Can view the status of their application.
    - Can view the feedback given by the recruiter.
- After a candidate creates an account, they can upload their resume. The resume should be in PDF format, and the system
  should extract the skills and experience from the resume and store them in the database.
- The system should have a search functionality that allows recruiters to search for candidates based on their skills
  and experience.
- The candidate should be able to validate the skills and experience extracted from their resume and update them if
  necessary.
- The system should have a notification system that sends an email to the candidate when they apply for a position, and
  to the recruiter when a candidate applies for a position.