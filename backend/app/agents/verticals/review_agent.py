"""Review Agent implementation for customer feedback and review management."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
import json
import logging
import random
from datetime import datetime, timedelta

from ..base import BaseAgent, AgentConfig, Department, AgentRole, AgentState

logger = logging.getLogger(__name__)

class ReviewAgent(BaseAgent):
    """Specialized agent for customer feedback, review management, and sentiment analysis."""
    
    def __init__(self, config: Dict[str, Any], memory_service, rag_service):
        default_config = {
            "id": "review_agent",
            "name": "Maya Patel",
            "role": AgentRole.REVIEW_AGENT,
            "department": Department.SUPPORT,
            "level": 3,
            "manager_id": "manager",
            "system_prompt": (
                "You are Maya Patel, Customer Feedback Specialist at AgentFlow Pro.\n"
                "You are empathetic, analytical, and customer-focused. Your expertise includes "
                "review monitoring, sentiment analysis, feedback collection, and customer satisfaction management. "
                "You understand the importance of customer feedback in business improvement and reputation management. "
                "You respond professionally to all feedback and work to turn negative experiences into positive outcomes."
            ),
            "tools": ["monitor_reviews", "generate_response", "collect_feedback", "analyze_sentiment"],
            "specializations": ["Review Monitoring", "Sentiment Analysis", "Feedback Collection", "Customer Satisfaction"],
            "performance_metrics": {
                "reviews_monitored": 0,
                "responses_generated": 0,
                "feedback_collected": 0,
                "average_rating": 0.0,
                "sentiment_score": 0.0,
                "response_time": 0.0
            },
            "personality": {
                "tone": "empathetic and professional",
                "communication_style": "understanding and solution-focused",
                "approach": "customer-centric and proactive"
            }
        }
        
        merged_config = {**default_config, **config}
        super().__init__(merged_config, memory_service, rag_service)
    
    async def _generate_response(self, state: AgentState, context: Dict[str, Any]) -> AIMessage:
        """Generate a response to the review/feedback query."""
        task = context.get("task_context", {})
        
        system_prompt = f"""
        {self.config.system_prompt}
        
        Current Task: {task.get('description', 'No task description')}
        
        Review Context:
        {json.dumps(context.get('review_data', {}), indent=2)}
        
        Performance Metrics:
        - Reviews monitored: {self.config.performance_metrics['reviews_monitored']}
        - Responses generated: {self.config.performance_metrics['responses_generated']}
        - Feedback collected: {self.config.performance_metrics['feedback_collected']}
        - Average rating: {self.config.performance_metrics['average_rating']:.1f}/5.0
        - Sentiment score: {self.config.performance_metrics['sentiment_score']:.1f}%
        - Average response time: {self.config.performance_metrics['response_time']:.1f} hours
        
        Guidelines:
        1. Monitor reviews across all platforms consistently
        2. Respond to feedback promptly and professionally
        3. Address negative feedback with empathy and solutions
        4. Thank customers for positive feedback
        5. Identify trends and patterns in customer feedback
        6. Escalate serious issues to appropriate teams
        7. Use feedback to drive business improvements
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            ("system", "Provide comprehensive review and feedback analysis:")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"messages": state.messages})
        
        # Update metrics
        if "review" in response.content.lower() or "feedback" in response.content.lower():
            self.config.performance_metrics["reviews_monitored"] += 1
        
        # Determine if escalation is needed
        if any(term in response.content.lower() for term in ["escalate", "manager", "crisis", "legal"]):
            state.escalate = True
            state.next_agent = "manager"
        
        return response
    
    @tool
    async def monitor_reviews(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor reviews and feedback across multiple platforms."""
        try:
            monitor_id = f"MON-{random.randint(10000, 99999)}"
            
            # Time period for monitoring
            hours_back = monitoring_config.get("hours_back", 24)
            start_time = datetime.now() - timedelta(hours=hours_back)
            
            review_monitoring = {
                "monitor_id": monitor_id,
                "monitoring_period": {
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "hours_monitored": hours_back
                },
                "platforms": {},
                "summary": {
                    "total_reviews": 0,
                    "new_reviews": 0,
                    "average_rating": 0.0,
                    "sentiment_breakdown": {
                        "positive": 0,
                        "neutral": 0,
                        "negative": 0
                    },
                    "response_required": 0,
                    "urgent_issues": 0
                },
                "alerts": [],
                "trending_topics": [],
                "generated_at": datetime.now().isoformat()
            }
            
            # Monitor each platform
            platforms = monitoring_config.get("platforms", ["google", "yelp", "trustpilot", "facebook", "app_store"])
            
            for platform in platforms:
                platform_data = {
                    "platform_name": platform,
                    "total_reviews": random.randint(10, 100),
                    "new_reviews": random.randint(0, 15),
                    "average_rating": random.uniform(3.5, 4.8),
                    "rating_distribution": {
                        "5_star": random.randint(40, 70),
                        "4_star": random.randint(15, 30),
                        "3_star": random.randint(5, 15),
                        "2_star": random.randint(2, 8),
                        "1_star": random.randint(1, 5)
                    },
                    "sentiment_analysis": {
                        "positive": random.uniform(60, 85),
                        "neutral": random.uniform(10, 25),
                        "negative": random.uniform(5, 20)
                    },
                    "recent_reviews": [],
                    "response_rate": random.uniform(75, 95),
                    "average_response_time": random.uniform(2, 24)  # hours
                }
                
                # Generate sample recent reviews
                for i in range(min(platform_data["new_reviews"], 5)):
                    review = {
                        "review_id": f"{platform.upper()}-{random.randint(1000, 9999)}",
                        "rating": random.randint(1, 5),
                        "title": f"Sample review title {i+1}",
                        "content": f"Sample review content for {platform} review {i+1}",
                        "reviewer": {
                            "name": f"Customer {i+1}",
                            "verified": random.choice([True, False]),
                            "review_count": random.randint(1, 50)
                        },
                        "date": (datetime.now() - timedelta(hours=random.randint(1, hours_back))).isoformat(),
                        "sentiment": random.choice(["positive", "neutral", "negative"]),
                        "keywords": random.sample(["service", "quality", "price", "support", "features"], 2),
                        "response_required": random.choice([True, False]),
                        "urgency": random.choice(["low", "medium", "high"])
                    }
                    platform_data["recent_reviews"].append(review)
                
                review_monitoring["platforms"][platform] = platform_data
                
                # Update summary
                review_monitoring["summary"]["total_reviews"] += platform_data["total_reviews"]
                review_monitoring["summary"]["new_reviews"] += platform_data["new_reviews"]
                
                # Count sentiment
                for review in platform_data["recent_reviews"]:
                    review_monitoring["summary"]["sentiment_breakdown"][review["sentiment"]] += 1
                    if review["response_required"]:
                        review_monitoring["summary"]["response_required"] += 1
                    if review["urgency"] == "high":
                        review_monitoring["summary"]["urgent_issues"] += 1
            
            # Calculate overall average rating
            if platforms:
                total_rating = sum(p["average_rating"] for p in review_monitoring["platforms"].values())
                review_monitoring["summary"]["average_rating"] = total_rating / len(platforms)
            
            # Generate alerts
            if review_monitoring["summary"]["average_rating"] < 3.5:
                review_monitoring["alerts"].append({
                    "type": "low_rating_alert",
                    "severity": "high",
                    "message": "Average rating has dropped below 3.5 stars",
                    "action_required": True
                })
            
            if review_monitoring["summary"]["urgent_issues"] > 3:
                review_monitoring["alerts"].append({
                    "type": "urgent_issues_alert",
                    "severity": "high",
                    "message": f"{review_monitoring['summary']['urgent_issues']} urgent issues require immediate attention",
                    "action_required": True
                })
            
            negative_percentage = (review_monitoring["summary"]["sentiment_breakdown"]["negative"] / 
                                 max(1, review_monitoring["summary"]["new_reviews"]) * 100)
            if negative_percentage > 25:
                review_monitoring["alerts"].append({
                    "type": "negative_sentiment_spike",
                    "severity": "medium",
                    "message": f"Negative sentiment at {negative_percentage:.1f}% - above normal threshold",
                    "action_required": True
                })
            
            # Identify trending topics
            all_keywords = []
            for platform_data in review_monitoring["platforms"].values():
                for review in platform_data["recent_reviews"]:
                    all_keywords.extend(review["keywords"])
            
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            review_monitoring["trending_topics"] = [
                {"topic": keyword, "mentions": count}
                for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Update metrics
            self.config.performance_metrics["reviews_monitored"] += review_monitoring["summary"]["new_reviews"]
            self.config.performance_metrics["average_rating"] = review_monitoring["summary"]["average_rating"]
            
            return review_monitoring
            
        except Exception as e:
            logger.error(f"Error monitoring reviews: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def generate_response(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate responses to customer reviews."""
        try:
            response_id = f"RESP-{random.randint(10000, 99999)}"
            
            review_rating = review_data.get("rating", 3)
            review_sentiment = review_data.get("sentiment", "neutral")
            review_content = review_data.get("content", "")
            
            response_generation = {
                "response_id": response_id,
                "review_id": review_data.get("review_id", ""),
                "platform": review_data.get("platform", ""),
                "review_details": {
                    "rating": review_rating,
                    "sentiment": review_sentiment,
                    "content": review_content,
                    "reviewer": review_data.get("reviewer", {}),
                    "date": review_data.get("date", "")
                },
                "response_strategy": self._determine_response_strategy(review_rating, review_sentiment),
                "generated_responses": [],
                "recommended_response": "",
                "tone_analysis": {},
                "follow_up_actions": [],
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat()
            }
            
            # Generate multiple response options
            response_templates = self._get_response_templates(review_rating, review_sentiment)
            
            for i, template in enumerate(response_templates[:3]):  # Generate up to 3 options
                response_option = {
                    "option_id": f"OPT-{i+1}",
                    "response_text": template["text"],
                    "tone": template["tone"],
                    "personalization_level": template["personalization"],
                    "includes_solution": template.get("includes_solution", False),
                    "includes_compensation": template.get("includes_compensation", False),
                    "estimated_effectiveness": random.uniform(0.7, 0.95)
                }
                response_generation["generated_responses"].append(response_option)
            
            # Select recommended response (highest effectiveness)
            if response_generation["generated_responses"]:
                best_response = max(response_generation["generated_responses"], 
                                  key=lambda x: x["estimated_effectiveness"])
                response_generation["recommended_response"] = best_response["response_text"]
                
                # Analyze tone of recommended response
                response_generation["tone_analysis"] = {
                    "primary_tone": best_response["tone"],
                    "empathy_level": random.uniform(0.6, 0.9),
                    "professionalism_score": random.uniform(0.8, 1.0),
                    "solution_focus": random.uniform(0.5, 0.9),
                    "brand_alignment": random.uniform(0.7, 0.95)
                }
            
            # Determine follow-up actions
            if review_rating <= 2:
                response_generation["follow_up_actions"] = [
                    "Schedule follow-up call with customer",
                    "Escalate to customer success team",
                    "Offer compensation or refund",
                    "Internal process review"
                ]
            elif review_rating == 3:
                response_generation["follow_up_actions"] = [
                    "Send follow-up email to address concerns",
                    "Monitor for additional feedback",
                    "Consider product improvement suggestions"
                ]
            elif review_rating >= 4:
                response_generation["follow_up_actions"] = [
                    "Thank customer via email",
                    "Request referral or testimonial",
                    "Share positive feedback with team"
                ]
            
            # Add compliance and approval workflow
            response_generation["approval_workflow"] = {
                "requires_approval": review_rating <= 2 or "legal" in review_content.lower(),
                "approver": "customer_success_manager" if review_rating <= 2 else None,
                "approval_status": "pending" if review_rating <= 2 else "auto_approved",
                "escalation_required": review_rating == 1 or any(word in review_content.lower() 
                                                               for word in ["lawsuit", "legal", "fraud", "scam"])
            }
            
            # Update metrics
            self.config.performance_metrics["responses_generated"] += 1
            
            return response_generation
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def collect_feedback(self, collection_config: Dict[str, Any]) -> Dict[str, Any]:
        """Collect customer feedback through various channels."""
        try:
            collection_id = f"FEEDBACK-{random.randint(10000, 99999)}"
            
            feedback_collection = {
                "collection_id": collection_id,
                "collection_type": collection_config.get("type", "survey"),  # survey, interview, nps, csat
                "title": collection_config.get("title", "Customer Feedback Collection"),
                "description": collection_config.get("description", ""),
                "target_audience": collection_config.get("target_audience", "all_customers"),
                "collection_method": collection_config.get("method", "email"),  # email, sms, in_app, phone
                "collection_period": {
                    "start_date": collection_config.get("start_date", datetime.now().strftime("%Y-%m-%d")),
                    "end_date": collection_config.get("end_date", (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")),
                    "duration_days": collection_config.get("duration_days", 14)
                },
                "questions": collection_config.get("questions", []),
                "response_tracking": {
                    "target_responses": collection_config.get("target_responses", 100),
                    "responses_received": 0,
                    "response_rate": 0.0,
                    "completion_rate": 0.0
                },
                "incentives": collection_config.get("incentives", {}),
                "collected_responses": [],
                "analysis_results": {},
                "status": "Active",
                "created_by": self.config.name,
                "created_at": datetime.now().isoformat()
            }
            
            # Add default questions based on collection type
            if not feedback_collection["questions"]:
                feedback_collection["questions"] = self._get_default_questions(collection_config.get("type", "survey"))
            
            # Simulate feedback collection if requested
            if collection_config.get("simulate_responses", False):
                num_responses = random.randint(10, 50)
                
                for i in range(num_responses):
                    response = {
                        "response_id": f"RESP-{random.randint(1000, 9999)}",
                        "customer_id": f"CUST-{random.randint(1000, 9999)}",
                        "submission_date": (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat(),
                        "channel": random.choice(["email", "in_app", "website", "phone"]),
                        "responses": {},
                        "completion_status": random.choice(["complete", "partial"]),
                        "time_spent_minutes": random.randint(2, 15)
                    }
                    
                    # Generate responses to questions
                    for question in feedback_collection["questions"]:
                        if question["type"] == "rating":
                            response["responses"][question["id"]] = random.randint(1, 5)
                        elif question["type"] == "nps":
                            response["responses"][question["id"]] = random.randint(0, 10)
                        elif question["type"] == "text":
                            response["responses"][question["id"]] = f"Sample text response {i+1}"
                        elif question["type"] == "multiple_choice":
                            response["responses"][question["id"]] = random.choice(question.get("options", ["Option A"]))
                        elif question["type"] == "boolean":
                            response["responses"][question["id"]] = random.choice([True, False])
                    
                    feedback_collection["collected_responses"].append(response)
                
                # Update tracking metrics
                feedback_collection["response_tracking"]["responses_received"] = num_responses
                feedback_collection["response_tracking"]["response_rate"] = (num_responses / 
                    feedback_collection["response_tracking"]["target_responses"] * 100)
                
                complete_responses = sum(1 for r in feedback_collection["collected_responses"] 
                                       if r["completion_status"] == "complete")
                feedback_collection["response_tracking"]["completion_rate"] = (complete_responses / num_responses * 100)
                
                # Generate analysis results
                feedback_collection["analysis_results"] = self._analyze_feedback_responses(
                    feedback_collection["collected_responses"], 
                    feedback_collection["questions"]
                )
            
            # Update metrics
            self.config.performance_metrics["feedback_collected"] += feedback_collection["response_tracking"]["responses_received"]
            
            return feedback_collection
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            return {"error": str(e)}
    
    @tool
    async def analyze_sentiment(self, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of customer feedback and reviews."""
        try:
            analysis_id = f"SENTIMENT-{random.randint(10000, 99999)}"
            
            text_data = analysis_request.get("text_data", [])
            analysis_type = analysis_request.get("analysis_type", "comprehensive")  # basic, comprehensive, trend
            
            sentiment_analysis = {
                "analysis_id": analysis_id,
                "analysis_type": analysis_type,
                "data_source": analysis_request.get("data_source", "reviews"),
                "text_samples_analyzed": len(text_data),
                "analysis_date": datetime.now().isoformat(),
                "overall_sentiment": {
                    "score": 0.0,  # -1 to 1 scale
                    "classification": "neutral",  # positive, neutral, negative
                    "confidence": 0.0
                },
                "sentiment_distribution": {
                    "positive": {"count": 0, "percentage": 0.0},
                    "neutral": {"count": 0, "percentage": 0.0},
                    "negative": {"count": 0, "percentage": 0.0}
                },
                "emotion_analysis": {},
                "key_themes": [],
                "sentiment_trends": [],
                "actionable_insights": [],
                "detailed_results": [],
                "generated_by": self.config.name
            }
            
            # Analyze each text sample
            for i, text in enumerate(text_data[:100]):  # Limit to 100 samples for demo
                # Simulate sentiment analysis
                sentiment_score = random.uniform(-1, 1)
                confidence = random.uniform(0.6, 0.95)
                
                if sentiment_score > 0.1:
                    classification = "positive"
                    sentiment_analysis["sentiment_distribution"]["positive"]["count"] += 1
                elif sentiment_score < -0.1:
                    classification = "negative"
                    sentiment_analysis["sentiment_distribution"]["negative"]["count"] += 1
                else:
                    classification = "neutral"
                    sentiment_analysis["sentiment_distribution"]["neutral"]["count"] += 1
                
                detailed_result = {
                    "text_id": f"TEXT-{i+1}",
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "sentiment_score": round(sentiment_score, 3),
                    "classification": classification,
                    "confidence": round(confidence, 3),
                    "key_phrases": random.sample([
                        "great service", "poor quality", "excellent support", 
                        "slow response", "highly recommend", "disappointed"
                    ], random.randint(1, 3)),
                    "emotions_detected": random.sample([
                        "joy", "anger", "frustration", "satisfaction", "excitement", "disappointment"
                    ], random.randint(1, 2))
                }
                
                sentiment_analysis["detailed_results"].append(detailed_result)
            
            # Calculate overall metrics
            if sentiment_analysis["detailed_results"]:
                total_score = sum(r["sentiment_score"] for r in sentiment_analysis["detailed_results"])
                sentiment_analysis["overall_sentiment"]["score"] = round(total_score / len(sentiment_analysis["detailed_results"]), 3)
                
                avg_confidence = sum(r["confidence"] for r in sentiment_analysis["detailed_results"])
                sentiment_analysis["overall_sentiment"]["confidence"] = round(avg_confidence / len(sentiment_analysis["detailed_results"]), 3)
                
                # Classify overall sentiment
                overall_score = sentiment_analysis["overall_sentiment"]["score"]
                if overall_score > 0.1:
                    sentiment_analysis["overall_sentiment"]["classification"] = "positive"
                elif overall_score < -0.1:
                    sentiment_analysis["overall_sentiment"]["classification"] = "negative"
                else:
                    sentiment_analysis["overall_sentiment"]["classification"] = "neutral"
            
            # Calculate percentages
            total_samples = len(sentiment_analysis["detailed_results"])
            if total_samples > 0:
                for sentiment_type in sentiment_analysis["sentiment_distribution"]:
                    count = sentiment_analysis["sentiment_distribution"][sentiment_type]["count"]
                    sentiment_analysis["sentiment_distribution"][sentiment_type]["percentage"] = round(count / total_samples * 100, 1)
            
            # Generate emotion analysis
            all_emotions = []
            for result in sentiment_analysis["detailed_results"]:
                all_emotions.extend(result["emotions_detected"])
            
            emotion_counts = {}
            for emotion in all_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            sentiment_analysis["emotion_analysis"] = {
                emotion: {"count": count, "percentage": round(count / len(all_emotions) * 100, 1)}
                for emotion, count in emotion_counts.items()
            }
            
            # Identify key themes
            all_phrases = []
            for result in sentiment_analysis["detailed_results"]:
                all_phrases.extend(result["key_phrases"])
            
            phrase_counts = {}
            for phrase in all_phrases:
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            
            sentiment_analysis["key_themes"] = [
                {"theme": phrase, "mentions": count, "sentiment_impact": random.choice(["positive", "negative", "neutral"])}
                for phrase, count in sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Generate actionable insights
            insights = []
            
            if sentiment_analysis["sentiment_distribution"]["negative"]["percentage"] > 30:
                insights.append("High negative sentiment detected - immediate action required")
            
            if sentiment_analysis["sentiment_distribution"]["positive"]["percentage"] > 70:
                insights.append("Strong positive sentiment - leverage for marketing and testimonials")
            
            if "poor quality" in phrase_counts and phrase_counts["poor quality"] > 3:
                insights.append("Quality issues mentioned frequently - review product/service quality")
            
            if "slow response" in phrase_counts and phrase_counts["slow response"] > 2:
                insights.append("Response time concerns - review customer service processes")
            
            sentiment_analysis["actionable_insights"] = insights
            
            # Update metrics
            self.config.performance_metrics["sentiment_score"] = sentiment_analysis["overall_sentiment"]["score"] * 100
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"error": str(e)}
    
    def _determine_response_strategy(self, rating: int, sentiment: str) -> Dict[str, Any]:
        """Determine the appropriate response strategy based on rating and sentiment."""
        if rating <= 2:
            return {
                "strategy": "damage_control",
                "priority": "high",
                "tone": "apologetic_and_solution_focused",
                "personalization": "high",
                "follow_up_required": True,
                "escalation_needed": True
            }
        elif rating == 3:
            return {
                "strategy": "improvement_focused",
                "priority": "medium",
                "tone": "understanding_and_helpful",
                "personalization": "medium",
                "follow_up_required": True,
                "escalation_needed": False
            }
        else:  # rating >= 4
            return {
                "strategy": "appreciation_and_engagement",
                "priority": "low",
                "tone": "grateful_and_friendly",
                "personalization": "medium",
                "follow_up_required": False,
                "escalation_needed": False
            }
    
    def _get_response_templates(self, rating: int, sentiment: str) -> List[Dict[str, Any]]:
        """Get response templates based on rating and sentiment."""
        if rating <= 2:
            return [
                {
                    "text": "Thank you for your feedback. We sincerely apologize for not meeting your expectations. We take your concerns seriously and would like to make this right. Please contact us directly so we can resolve this issue promptly.",
                    "tone": "apologetic",
                    "personalization": "high",
                    "includes_solution": True,
                    "includes_compensation": True
                },
                {
                    "text": "We're sorry to hear about your experience. Your feedback is valuable to us and helps us improve. We'd appreciate the opportunity to discuss this further and find a solution that works for you.",
                    "tone": "understanding",
                    "personalization": "medium",
                    "includes_solution": True,
                    "includes_compensation": False
                }
            ]
        elif rating == 3:
            return [
                {
                    "text": "Thank you for taking the time to share your feedback. We appreciate your honest review and are always looking for ways to improve. We'd love to hear more about how we can better serve you in the future.",
                    "tone": "appreciative",
                    "personalization": "medium",
                    "includes_solution": False,
                    "includes_compensation": False
                }
            ]
        else:  # rating >= 4
            return [
                {
                    "text": "Thank you so much for your wonderful review! We're thrilled to hear about your positive experience. Your feedback means the world to us and motivates our team to continue delivering excellent service.",
                    "tone": "grateful",
                    "personalization": "medium",
                    "includes_solution": False,
                    "includes_compensation": False
                },
                {
                    "text": "We're so happy you had a great experience with us! Thank you for taking the time to share your positive feedback. We truly appreciate customers like you!",
                    "tone": "enthusiastic",
                    "personalization": "low",
                    "includes_solution": False,
                    "includes_compensation": False
                }
            ]
    
    def _get_default_questions(self, collection_type: str) -> List[Dict[str, Any]]:
        """Get default questions based on collection type."""
        question_sets = {
            "survey": [
                {"id": "overall_satisfaction", "type": "rating", "question": "How satisfied are you with our service overall?", "scale": "1-5"},
                {"id": "recommendation", "type": "nps", "question": "How likely are you to recommend us to a friend or colleague?", "scale": "0-10"},
                {"id": "improvement_suggestions", "type": "text", "question": "What could we do to improve your experience?"}
            ],
            "nps": [
                {"id": "nps_score", "type": "nps", "question": "How likely are you to recommend our company to a friend or colleague?", "scale": "0-10"},
                {"id": "nps_reason", "type": "text", "question": "What is the primary reason for your score?"}
            ],
            "csat": [
                {"id": "satisfaction", "type": "rating", "question": "How satisfied were you with your recent experience?", "scale": "1-5"},
                {"id": "service_quality", "type": "rating", "question": "How would you rate the quality of service you received?", "scale": "1-5"},
                {"id": "additional_comments", "type": "text", "question": "Any additional comments or suggestions?"}
            ]
        }
        return question_sets.get(collection_type, question_sets["survey"])
    
    def _analyze_feedback_responses(self, responses: List[Dict[str, Any]], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze collected feedback responses."""
        analysis = {
            "response_summary": {
                "total_responses": len(responses),
                "complete_responses": sum(1 for r in responses if r["completion_status"] == "complete"),
                "average_time_spent": sum(r["time_spent_minutes"] for r in responses) / len(responses) if responses else 0
            },
            "question_analysis": {},
            "key_insights": [],
            "recommendations": []
        }
        
        # Analyze each question
        for question in questions:
            question_id = question["id"]
            question_responses = [r["responses"].get(question_id) for r in responses if question_id in r["responses"]]
            
            if question["type"] in ["rating", "nps"]:
                if question_responses:
                    numeric_responses = [r for r in question_responses if isinstance(r, (int, float))]
                    if numeric_responses:
                        analysis["question_analysis"][question_id] = {
                            "average_score": sum(numeric_responses) / len(numeric_responses),
                            "response_count": len(numeric_responses),
                            "distribution": {str(i): numeric_responses.count(i) for i in range(0, 11) if i in numeric_responses}
                        }
            
            elif question["type"] == "text":
                text_responses = [r for r in question_responses if r and isinstance(r, str)]
                analysis["question_analysis"][question_id] = {
                    "response_count": len(text_responses),
                    "common_themes": ["service quality", "response time", "user experience"]  # Simplified
                }
        
        # Generate insights
        if "overall_satisfaction" in analysis["question_analysis"]:
            avg_satisfaction = analysis["question_analysis"]["overall_satisfaction"].get("average_score", 0)
            if avg_satisfaction >= 4:
                analysis["key_insights"].append("High customer satisfaction - maintain current service levels")
            elif avg_satisfaction < 3:
                analysis["key_insights"].append("Low satisfaction scores - immediate improvement needed")
        
        return analysis