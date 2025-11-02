class HOSCalculator:
    """Calculate Hours of Service compliance for 70-hour/8-day cycle"""

    def __init__(self, current_cycle_used):
        self.current_cycle_used = current_cycle_used
        self.max_cycle_hours = 70.0
        self.max_driving_hours = 11.0
        self.max_on_duty_hours = 14.0
        self.required_break_hours = 0.5

    def calculate_compliance(self, total_distance, driving_time):
        """Calculate HOS compliance for the trip"""
        hours_available = self.max_cycle_hours - self.current_cycle_used

        # Calculate required breaks
        rest_breaks = int(driving_time / 8.0)

        # Add 10-hour rest periods for multi-day trips
        if driving_time > self.max_driving_hours:
            days_needed = int(driving_time / self.max_driving_hours) + 1
            rest_breaks += (days_needed - 1)

        # Calculate total hours
        break_time = (rest_breaks * 0.5) + (max(0, int(driving_time / 11.0)) * 10.0)
        total_hours_used = self.current_cycle_used + driving_time + break_time + 2.0

        compliant = total_hours_used <= self.max_cycle_hours

        return {
            'hours_available': round(hours_available, 1),
            'total_hours_used': round(total_hours_used, 1),
            'rest_breaks': rest_breaks,
            'compliant': compliant,
            'driving_time': round(driving_time, 1),
            'break_time': round(break_time, 1)
        }