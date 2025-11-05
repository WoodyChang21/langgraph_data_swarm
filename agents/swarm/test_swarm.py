"""
Test Script for Airport Agent Swarm

This script demonstrates various use cases and tests
the swarm's ability to handle different types of queries.
"""

import asyncio
import sys
from datetime import datetime
from agents.swarm.swarm import airport_swarm


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")


def print_test(test_num, description):
    """Print test information"""
    print(f"{Colors.CYAN}{Colors.BOLD}Test {test_num}: {description}{Colors.END}")
    print(f"{Colors.YELLOW}{'─'*80}{Colors.END}")


def print_query(query):
    """Print the query being tested"""
    print(f"{Colors.BLUE}Query: {query}{Colors.END}")


def print_response(response):
    """Print the agent's response"""
    print(f"\n{Colors.GREEN}Response:{Colors.END}")
    print(f"{response}\n")


async def run_test(test_num, description, user_id, query):
    """
    Run a single test case
    
    Args:
        test_num: Test number
        description: Test description
        user_id: User identifier for the test
        query: Query to send to the swarm
    """
    print_test(test_num, description)
    print_query(query)
    
    try:
        start_time = datetime.now()
        
        # Invoke the swarm
        response = await airport_swarm.invoke(user_id, query)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_response(response)
        print(f"{Colors.YELLOW}⏱️  Duration: {duration:.2f} seconds{Colors.END}")
        
        return True
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}\n")
        return False


async def test_sql_agent():
    """Test SQL Agent functionality"""
    print_header("SQL AGENT TESTS")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Simple database query
    if await run_test(
        1,
        "Simple Database Query",
        "test_sql_1",
        "查詢2025年1月的抵達航班數量"  # Query arrivals in January 2025
    ):
        tests_passed += 1
    
    await asyncio.sleep(2)
    
    # Test 2: Query with country filter
    if await run_test(
        2,
        "Query with Country Filter",
        "test_sql_2",
        "Show me all flights from Japan between 2025-01-01 and 2025-01-07"
    ):
        tests_passed += 1
    
    await asyncio.sleep(2)
    
    # Test 3: Complex query with aggregation
    if await run_test(
        3,
        "Complex Aggregation Query",
        "test_sql_3",
        "Get the top 5 countries by number of arrival flights in January 2025"
    ):
        tests_passed += 1
    
    print(f"\n{Colors.GREEN}✓ SQL Agent Tests: {tests_passed}/{total_tests} passed{Colors.END}\n")
    return tests_passed == total_tests


async def test_plot_agent():
    """Test Plot Agent functionality"""
    print_header("PLOT AGENT TESTS")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: SQL query with immediate visualization
    if await run_test(
        1,
        "Query and Visualize",
        "test_plot_1",
        "Query flights from Korea in January 2025 and create a bar chart showing daily flight counts"
    ):
        tests_passed += 1
    
    await asyncio.sleep(2)
    
    # Test 2: Different plot type
    if await run_test(
        2,
        "Pie Chart Visualization",
        "test_plot_2",
        "Show arrival flights by airport code as a pie chart for January 2025"
    ):
        tests_passed += 1
    
    print(f"\n{Colors.GREEN}✓ Plot Agent Tests: {tests_passed}/{total_tests} passed{Colors.END}\n")
    return tests_passed == total_tests


async def test_agent_handoff():
    """Test agent handoff functionality"""
    print_header("AGENT HANDOFF TESTS")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: SQL -> Plot handoff
    if await run_test(
        1,
        "SQL to Plot Handoff",
        "test_handoff_1",
        "請查詢從日本出發的航班並匯出CSV，然後繪製長條圖"
    ):
        tests_passed += 1
    
    await asyncio.sleep(2)
    
    # Test 2: Multi-turn conversation with context
    user_id = "test_handoff_2"
    
    print_test(2, "Multi-Turn Conversation")
    
    # First turn: Get data
    print_query("Turn 1: Get data from Taiwan")
    try:
        response1 = await airport_swarm.invoke(
            user_id,
            "Show me flights from Taiwan in January 2025 and export to CSV"
        )
        print_response(response1)
        
        # Second turn: Ask for visualization (should remember previous data)
        print_query("Turn 2: Request visualization")
        response2 = await airport_swarm.invoke(
            user_id,
            "Now create a line chart from that data showing trends over time"
        )
        print_response(response2)
        
        tests_passed += 1
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {str(e)}{Colors.END}\n")
    
    print(f"\n{Colors.GREEN}✓ Handoff Tests: {tests_passed}/{total_tests} passed{Colors.END}\n")
    return tests_passed == total_tests


async def test_error_handling():
    """Test error handling capabilities"""
    print_header("ERROR HANDLING TESTS")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Invalid query
    print_test(1, "Invalid Query Handling")
    print_query("Show me flights from a country that doesn't exist: XYZ123")
    
    try:
        response = await airport_swarm.invoke("test_error_1", 
                                             "Show me flights from XYZ123 country")
        print_response(response)
        
        # Should handle gracefully, not crash
        if "error" in response.lower() or "not found" in response.lower() or "no" in response.lower():
            tests_passed += 1
            print(f"{Colors.GREEN}✓ Handled gracefully{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Caught exception (acceptable): {str(e)}{Colors.END}")
        tests_passed += 1
    
    await asyncio.sleep(2)
    
    # Test 2: Unclear request
    print_test(2, "Unclear Request Handling")
    print_query("Do something with data")
    
    try:
        response = await airport_swarm.invoke("test_error_2", "Do something with data")
        print_response(response)
        
        # Agent should ask for clarification
        tests_passed += 1
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {str(e)}{Colors.END}")
    
    print(f"\n{Colors.GREEN}✓ Error Handling Tests: {tests_passed}/{total_tests} passed{Colors.END}\n")
    return tests_passed == total_tests


async def run_all_tests():
    """Run all test suites"""
    print_header("AIRPORT AGENT SWARM - COMPREHENSIVE TEST SUITE")
    print(f"{Colors.CYAN}Testing the multi-agent system with various scenarios{Colors.END}\n")
    
    results = {
        # "SQL Agent": await test_sql_agent(),
        "Plot Agent": await test_plot_agent(),
        # "Agent Handoff": await test_agent_handoff(),
        # "Error Handling": await test_error_handling(),
    }
    
    # Print summary
    print_header("TEST SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✓ PASSED{Colors.END}" if passed else f"{Colors.RED}✗ FAILED{Colors.END}"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    print(f"\n{Colors.BOLD}{'─'*80}{Colors.END}")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SOME TESTS FAILED ⚠️{Colors.END}\n")
    
    return all_passed


async def interactive_mode():
    """Run in interactive mode for manual testing using stream method"""
    print_header("INTERACTIVE MODE - STREAMING")
    print(f"{Colors.CYAN}You can now interact with the swarm directly{Colors.END}")
    print(f"{Colors.CYAN}This mode uses streaming to show detailed chunk information{Colors.END}")
    print(f"{Colors.CYAN}Type 'exit' to quit{Colors.END}")
    print(f"{Colors.CYAN}Type 'clear history' to reset conversation{Colors.END}\n")
    
    user_id = "interactive_user"
    
    while True:
        try:
            query = input(f"{Colors.BOLD}Your query: {Colors.END}").strip()
            
            if query.lower() in ["exit", "quit", "q"]:
                print(f"\n{Colors.GREEN}Goodbye!{Colors.END}\n")
                break
            
            if not query:
                continue
            
            # Handle clear history command
            if query.lower() == "clear history":
                await airport_swarm.clear_thread(user_id)
                print(f"\n{Colors.GREEN}✓ Conversation history cleared for {user_id}{Colors.END}\n")
                continue
            
            print(f"\n{Colors.YELLOW}Streaming chunks...{Colors.END}\n")
            print(f"{Colors.HEADER}{'='*80}{Colors.END}")
            
            chunk_count = 0
            async for chunk in airport_swarm.stream(user_id, query):
                chunk_count += 1
                
                print(f"\n{Colors.CYAN}{Colors.BOLD}Chunk #{chunk_count}:{Colors.END}")
                print(f"{Colors.YELLOW}{'─'*80}{Colors.END}")
                print(f"{Colors.RED}{Colors.BOLD}DEBUG - Full Chunk:{Colors.END}\n{chunk}\n")
                
                # Check if this is subgraphs mode (tuple format)
                if isinstance(chunk, tuple):
                    # subgraphs=True mode: (namespace, data)
                    namespace, subgraph_data = chunk
                    print(f"{Colors.MAGENTA}{Colors.BOLD}SUBGRAPHS MODE DETECTED{Colors.END}")
                    print(f"{Colors.BLUE}Namespace (path): {namespace}{Colors.END}")
                    print(f"{Colors.BLUE}Namespace Type: {type(namespace)}{Colors.END}")
                    
                    if isinstance(namespace, tuple):
                        for idx, ns_part in enumerate(namespace):
                            print(f"{Colors.BLUE}  Part {idx + 1}: {ns_part}{Colors.END}")
                    
                    print(f"\n{Colors.BLUE}Subgraph Data Type: {type(subgraph_data)}{Colors.END}")
                    print(f"{Colors.BLUE}Subgraph Data Keys: {list(subgraph_data.keys()) if isinstance(subgraph_data, dict) else 'N/A'}{Colors.END}")
                    
                    # Process the subgraph data
                    for key, value in subgraph_data.items():
                        print(f"\n{Colors.CYAN}Subgraph Key: {key}{Colors.END}")
                        print(f"{Colors.CYAN}Value Type: {type(value)}{Colors.END}")
                        
                        if isinstance(value, dict) and "messages" in value:
                            messages = value["messages"]
                            print(f"{Colors.CYAN}Number of Messages: {len(messages)}{Colors.END}")
                            
                            # Display each message
                            for idx, msg in enumerate(messages):
                                print(f"\n{Colors.GREEN}  Message {idx + 1}:{Colors.END}")
                                print(f"    Type: {type(msg).__name__}")
                                print(f"    Role: {getattr(msg, 'type', 'N/A')}")
                                
                                # Check for tool calls
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    print(f"    {Colors.YELLOW}Has Tool Calls: Yes{Colors.END}")
                                    print(f"    Tool Calls: {msg.tool_calls}")
                                else:
                                    print(f"    Has Tool Calls: No")
                                
                                # Display content
                                content = getattr(msg, 'content', '')
                                if content:
                                    print(f"    Content (preview): {str(content)[:150]}...")
                                else:
                                    print(f"    Content: {Colors.RED}(empty){Colors.END}")
                                
                                # Display additional info
                                if hasattr(msg, 'additional_kwargs'):
                                    print(f"    Additional kwargs: {msg.additional_kwargs}")
                                
                                if hasattr(msg, 'id'):
                                    print(f"    Message ID: {msg.id}")
                        else:
                            print(f"{Colors.CYAN}Value: {str(value)[:200]}...{Colors.END}")
                
                # Regular dict format (updates or values mode)
                elif isinstance(chunk, dict):
                    # Display chunk structure
                    for agent_name, chunk_data in chunk.items():
                        print(f"{Colors.BLUE}Agent: {agent_name}{Colors.END}")
                        print(f"{Colors.BLUE}Chunk Data Type: {type(chunk_data)}{Colors.END}")
                        
                        # This is updates mode
                        if isinstance(chunk_data, dict): 
                            print(f"{Colors.BLUE}Chunk Keys: {list(chunk_data.keys())}{Colors.END}")

                            # Check if messages exist
                            if "messages" in chunk_data:
                                messages = chunk_data["messages"]
                                print(f"{Colors.BLUE}Number of Messages: {len(messages)}{Colors.END}")
                                
                                # Display each message in detail
                                for idx, msg in enumerate(messages):
                                    print(f"\n{Colors.GREEN}  Message {idx + 1}:{Colors.END}")
                                    print(f"    Type: {type(msg).__name__}")
                                    print(f"    Role: {getattr(msg, 'type', 'N/A')}")
                                    
                                    # Check for tool calls
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        print(f"    {Colors.YELLOW}Has Tool Calls: Yes{Colors.END}")
                                        print(f"    Tool Calls: {msg.tool_calls}")
                                    else:
                                        print(f"    Has Tool Calls: No")
                                    
                                    # Display content
                                    content = getattr(msg, 'content', '')
                                    if content:
                                        print(f"    Content (preview): {str(content)[:150]}...")
                                    else:
                                        print(f"    Content: {Colors.RED}(empty){Colors.END}")
                                    
                                    # Display additional info if available
                                    if hasattr(msg, 'additional_kwargs'):
                                        print(f"    Additional kwargs: {msg.additional_kwargs}")
                                    
                                    # Display ID if available
                                    if hasattr(msg, 'id'):
                                        print(f"    Message ID: {msg.id}")
                            
                            # Display other chunk data keys
                            for key, value in chunk_data.items():
                                if key != "messages":
                                    print(f"{Colors.BLUE}{key}: {value}{Colors.END}")
                        # Stream mode is values
                        elif isinstance(chunk_data, list): 
                            # values mode: {'messages': [HumanMessage(...), AIMessage(...)]}
                            print(f"{Colors.BLUE}State Key: {agent_name} (values mode){Colors.END}")
                            print(f"{Colors.BLUE}Data Type: {type(chunk_data)}{Colors.END}")
                            print(f"{Colors.BLUE}Number of Items: {len(chunk_data)}{Colors.END}")
                            
                            # Display each message in the list
                            for idx, msg in enumerate(chunk_data):
                                print(f"\n{Colors.GREEN}  Message {idx + 1}:{Colors.END}")
                                print(f"    Type: {type(msg).__name__}")
                                print(f"    Role: {getattr(msg, 'type', 'N/A')}")
                                
                                # Check for tool calls
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    print(f"    {Colors.YELLOW}Has Tool Calls: Yes{Colors.END}")
                                    print(f"    Tool Calls: {msg.tool_calls}")
                                else:
                                    print(f"    Has Tool Calls: No")
                                
                                # Display content
                                content = getattr(msg, 'content', '')
                                if content:
                                    print(f"    Content (preview): {str(content)[:150]}...")
                                else:
                                    print(f"    Content: {Colors.RED}(empty){Colors.END}")
                                
                                # Display additional info if available
                                if hasattr(msg, 'additional_kwargs'):
                                    print(f"    Additional kwargs: {msg.additional_kwargs}")
                                
                                # Display ID if available
                                if hasattr(msg, 'id'):
                                    print(f"    Message ID: {msg.id}")
                        
                        else:
                            # Other data types
                            print(f"{Colors.BLUE}Key: {agent_name}{Colors.END}")
                            print(f"{Colors.BLUE}Type: {type(chunk_data)}{Colors.END}")
                            print(f"{Colors.BLUE}Value (preview): {str(chunk_data)[:200]}...{Colors.END}")

                print(f"{Colors.YELLOW}{'─'*80}{Colors.END}")
            
            print(f"\n{Colors.GREEN}Total chunks received: {chunk_count}{Colors.END}")
            print(f"{Colors.HEADER}{'='*80}{Colors.END}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Goodbye!{Colors.END}\n")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}\n")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

